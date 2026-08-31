"""OpenAI Responses API adapter for Trubot."""

from __future__ import annotations

import logging
import re
from collections.abc import Sequence

from openai import AsyncOpenAI
from openai.types.responses import EasyInputMessageParam, ResponseInputParam

from trubot.conversation import ConversationMessage, ReplyMode
from trubot.personality import instructions_for

logger = logging.getLogger(__name__)

_SPEAKER_PREFIX = re.compile(
    r"^(?:trubot|andrew(?:[.\s]+truax)?|truax)\s*:\s*",
    flags=re.IGNORECASE,
)
_PROMPT_CACHE_KEY = "wcb-trubot-personality-v4"
_NO_REPLY = "<NO_REPLY>"

_TARGET_LABELS = {
    ReplyMode.DIRECT: "CURRENT MESSAGE",
    ReplyMode.FOLLOW_UP: "LATEST MESSAGE",
    ReplyMode.REACTION: "REACTION TARGET",
}


class ResponderError(RuntimeError):
    """Base error for a response that cannot be posted."""


class EmptyResponseError(ResponderError):
    """Raised when the model returns no usable text."""


class OpenAITruaxResponder:
    def __init__(
        self,
        client: AsyncOpenAI,
        *,
        model: str,
        max_output_tokens: int,
    ) -> None:
        self._client = client
        self._model = model
        self._max_output_tokens = max_output_tokens

    async def reply(
        self,
        messages: Sequence[ConversationMessage],
        *,
        mode: ReplyMode,
        safety_id: str,
        target: str | None = None,
    ) -> str | None:
        model_input: ResponseInputParam = [
            EasyInputMessageParam(role=message.role, content=message.content)
            for message in messages
        ]
        if target:
            focused_input = EasyInputMessageParam(
                role="user",
                content=_format_target(mode, target),
            )
            if (
                mode in {ReplyMode.DIRECT, ReplyMode.FOLLOW_UP}
                and messages
                and messages[-1].role == "user"
                and messages[-1].content == target
            ):
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
        response = await self._client.responses.create(
            model=self._model,
            instructions=instructions_for(mode),
            input=model_input,
            reasoning={"effort": "none"},
            text={"verbosity": "low"},
            max_output_tokens=self._max_output_tokens,
            prompt_cache_key=_PROMPT_CACHE_KEY,
            safety_identifier=safety_id,
            store=False,
        )
        reply = normalize_reply(response.output_text)
        if mode is ReplyMode.FOLLOW_UP and reply.casefold() == _NO_REPLY.casefold():
            logger.info("Trubot declined follow-up candidate")
            return None
        if not reply:
            raise EmptyResponseError("OpenAI returned an empty text response")
        logger.info("Generated Trubot response mode=%s characters=%d", mode.value, len(reply))
        return reply

    async def close(self) -> None:
        await self._client.close()


def _format_target(mode: ReplyMode, target: str) -> str:
    label = _TARGET_LABELS.get(mode, "CURRENT MESSAGE")
    if mode is ReplyMode.FOLLOW_UP:
        return (
            f"{label} — decide whether this is addressed to Trubot; "
            f"answer or abstain as instructed:\n{target}"
        )
    return f"{label} — answer this now; earlier messages are context only:\n{target}"


def normalize_reply(reply: str | None) -> str:
    """Remove an accidental speaker label while preserving the authored line."""

    if not reply:
        return ""
    return _SPEAKER_PREFIX.sub("", reply.strip(), count=1).strip()
