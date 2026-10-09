"""OpenAI Responses API adapter for Trubot."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError
from openai.types.responses import (
    EasyInputMessageParam,
    Response,
    ResponseInputMessageContentListParam,
    ResponseInputParam,
)
from openai.types.responses.response_create_params import ResponseCreateParamsNonStreaming

from trubot.budget import NANODOLLARS, BudgetUnavailable, UsageLedger
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.personality import instructions_for
from trubot.vision import IMAGE_TOKEN_BOUND, MAX_IMAGES

logger = logging.getLogger(__name__)

_SPEAKER_PREFIX = re.compile(
    r"^(?:trubot|andrew(?:[.\s]+truax)?|truax)\s*:\s*",
    flags=re.IGNORECASE,
)
_PROMPT_CACHE_KEY = "wcb-trubot-personality-v9"
_NO_REPLY = "<NO_REPLY>"

_TARGET_LABELS = {
    ReplyMode.DIRECT: "CURRENT MESSAGE",
    ReplyMode.FOLLOW_UP: "LATEST MESSAGE",
    ReplyMode.REACTION: "REACTION TARGET",
}


class ResponderError(RuntimeError):
    """Base error for a response that cannot be posted."""


class StudyContextExceeded(ResponderError):
    """A study packet exceeds its existing request bound."""


class StudyResponseInvalid(ResponderError):
    """A study result is incomplete or cannot be decoded as an object."""


class EmptyResponseError(ResponderError):
    """Raised when the model returns no usable text."""


class OpenAITruaxResponder:
    def __init__(
        self,
        client: AsyncOpenAI,
        *,
        model: str,
        max_output_tokens: int,
        budget: UsageLedger,
        max_retries: int = 0,
        purpose: str = "runtime",
    ) -> None:
        self._client = client.with_options(max_retries=0)
        self._model = model
        self._max_output_tokens = max_output_tokens
        self._budget = budget
        self._max_retries = max_retries
        self._purpose = purpose

    async def reply(
        self,
        messages: Sequence[ConversationMessage],
        *,
        mode: ReplyMode,
        safety_id: str,
        target: str | None = None,
    ) -> str | None:
        model_input: ResponseInputParam = [_message_input(message) for message in messages]
        if target:
            focused_input = _message_input(
                ConversationMessage(
                    "user",
                    _format_target(mode, target),
                    messages[-1].images if messages and messages[-1].content == target else (),
                )
            )
            if messages and messages[-1].role == "user" and messages[-1].content == target:
                model_input[-1] = focused_input
            else:
                model_input.append(focused_input)
        if not model_input:
            raise ResponderError("Cannot generate a reply without conversation context")

        logger.info(
            "Requesting Trubot response model=%s mode=%s context_messages=%d",
            self._model,
            mode.value,
            len(messages),
        )
        instructions = instructions_for(mode)
        output_bound = (
            self._max_output_tokens
            if mode is ReplyMode.FOLLOW_UP
            else min(self._max_output_tokens, 180)
        )
        image_count = sum(len(message.images) for message in messages)
        if image_count > MAX_IMAGES:
            raise ResponderError("Too many response images")
        # Base64 bytes are not text tokens. Reserve text framing separately and
        # a deliberately conservative bound for each actual image input.
        text_input = [{"role": m.role, "content": m.content} for m in messages]
        if target:
            text_input.append({"role": "user", "content": _format_target(mode, target)})
        input_bound = (
            len(
                json.dumps(
                    {"instructions": instructions, "input": text_input}, ensure_ascii=False
                ).encode("utf-8")
            )
            + 4096
            + image_count * IMAGE_TOKEN_BOUND
        )
        response = await self._generate(
            input_bound=input_bound,
            output_bound=output_bound,
            mode=mode,
            request=ResponseCreateParamsNonStreaming(
                model=self._model,
                service_tier="default",
                instructions=instructions,
                input=model_input,
                reasoning={"effort": "low" if mode is ReplyMode.FOLLOW_UP else "none"},
                text={"verbosity": "low"},
                max_output_tokens=output_bound,
                prompt_cache_key=_PROMPT_CACHE_KEY,
                safety_identifier=safety_id,
                store=False,
            ),
        )
        reply = normalize_reply(response.output_text)
        if mode is ReplyMode.FOLLOW_UP and reply.casefold() == _NO_REPLY.casefold():
            logger.info("Trubot declined follow-up candidate")
            return None
        if not reply:
            raise EmptyResponseError("OpenAI returned an empty text response")
        logger.info("Generated Trubot response mode=%s characters=%d", mode.value, len(reply))
        return reply

    async def study_json(
        self,
        *,
        instructions: str,
        payload: dict[str, Any],
        schema: dict[str, Any],
        name: str,
        source_check: Callable[[], Awaitable[None]] | None = None,
    ) -> dict[str, Any]:
        """One bounded maintenance attempt. No retries, tools, or stored response."""
        content = json.dumps(payload, ensure_ascii=False)
        size = len(json.dumps([instructions, content, schema], ensure_ascii=False).encode())
        if size > 16_000:
            raise StudyContextExceeded("Study context exceeds its spending bound")
        response = await self._generate(
            input_bound=size + 4096,
            output_bound=1024,
            mode=ReplyMode.DIRECT,
            purpose="maintenance",
            retry_limit=0,
            before_request=source_check,
            request=ResponseCreateParamsNonStreaming(
                model=self._model,
                service_tier="default",
                instructions=instructions,
                input=[{"role": "user", "content": content}],
                reasoning={"effort": "none"},
                text={
                    "verbosity": "low",
                    "format": {
                        "type": "json_schema",
                        "name": name,
                        "strict": True,
                        "schema": schema,
                    },
                },
                max_output_tokens=1024,
                store=False,
                prompt_cache_key="wcb-trubot-distillation-v1",
            ),
        )
        if getattr(response, "status", "completed") != "completed":
            raise StudyResponseInvalid("Incomplete study response")
        try:
            parsed = json.loads(response.output_text)
            if not isinstance(parsed, dict):
                raise ValueError("Object required")
            return parsed
        except (ValueError, TypeError) as error:
            raise StudyResponseInvalid("Invalid study response") from error

    async def _generate(
        self,
        *,
        input_bound: int,
        output_bound: int,
        mode: ReplyMode,
        request: ResponseCreateParamsNonStreaming,
        purpose: str | None = None,
        retry_limit: int | None = None,
        before_request: Callable[[], Awaitable[None]] | None = None,
    ) -> Response:
        retries = self._max_retries if retry_limit is None else retry_limit
        for attempt in range(retries + 1):
            # Atomic commit completes before any provider I/O, across channels/processes.
            reservation = await asyncio.to_thread(
                self._budget.reserve,
                model=self._model,
                input_bound=input_bound,
                output_bound=output_bound,
                purpose=purpose or self._purpose,
                mode=mode.value,
            )
            try:
                if before_request is not None:
                    await before_request()
                response = await self._client.responses.create(**request)
            except asyncio.CancelledError:
                # A committed pending reservation survives cancellation and crashes.
                raise
            except Exception as error:
                await asyncio.to_thread(self._budget.uncertain, reservation)
                retryable = isinstance(error, APIConnectionError | RateLimitError) or (
                    isinstance(error, APIStatusError) and error.status_code >= 500
                )
                if not retryable or attempt == retries:
                    raise
                await asyncio.sleep(min(0.5 * 2**attempt, 8))
                continue
            usage = response.usage
            if usage is None:
                await asyncio.to_thread(self._budget.uncertain, reservation)
                logger.warning("Provider usage missing; full spending reservation retained")
            else:
                cost = await asyncio.to_thread(
                    self._budget.settle,
                    reservation,
                    input_tokens=usage.input_tokens,
                    cached_input_tokens=usage.input_tokens_details.cached_tokens,
                    output_tokens=usage.output_tokens,
                )
                logger.info(
                    "API usage model=%s input_tokens=%d cached_input_tokens=%d output_tokens=%d "
                    "estimated_usd=%.9f purpose=%s",
                    self._model,
                    usage.input_tokens,
                    usage.input_tokens_details.cached_tokens,
                    usage.output_tokens,
                    cost / NANODOLLARS,
                    purpose or self._purpose,
                )
            return response
        raise BudgetUnavailable("No accounted API attempt completed")

    async def close(self) -> None:
        await self._client.close()


def _message_input(message: ConversationMessage) -> EasyInputMessageParam:
    if not message.images:
        return EasyInputMessageParam(role=message.role, content=message.content)
    parts: ResponseInputMessageContentListParam = [{"type": "input_text", "text": message.content}]
    for image in message.images:
        parts.append({"type": "input_text", "text": image.description})
        parts.append({"type": "input_image", "image_url": image.data_url, "detail": "high"})
    return EasyInputMessageParam(role=message.role, content=parts)


def _format_target(mode: ReplyMode, target: str) -> str:
    label = _TARGET_LABELS.get(mode, "CURRENT MESSAGE")
    if mode is ReplyMode.FOLLOW_UP:
        return (
            f"{label} - decide whether this is addressed to Trubot; "
            f"answer or abstain as instructed:\n{target}"
        )
    return f"{label} - answer this now; earlier messages are context only:\n{target}"


def normalize_reply(reply: str | None) -> str:
    """Remove an accidental speaker label while preserving the authored line."""

    if not reply:
        return ""
    return _SPEAKER_PREFIX.sub("", reply.strip(), count=1).strip()
