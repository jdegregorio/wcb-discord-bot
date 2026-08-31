from types import SimpleNamespace
from typing import Any, cast

import pytest
from openai import AsyncOpenAI

from trubot.conversation import ConversationMessage, ReplyMode
from trubot.openai_responder import (
    EmptyResponseError,
    OpenAITruaxResponder,
    ResponderError,
    normalize_reply,
)


class FakeResponses:
    def __init__(self, output_text: str | None) -> None:
        self.output_text = output_text
        self.request: dict[str, Any] | None = None

    async def create(self, **request: Any) -> SimpleNamespace:
        self.request = request
        return SimpleNamespace(output_text=self.output_text)


class FakeOpenAI:
    def __init__(self, output_text: str | None = "Hot") -> None:
        self.responses = FakeResponses(output_text)
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def make_responder(fake: FakeOpenAI) -> OpenAITruaxResponder:
    return OpenAITruaxResponder(
        cast(AsyncOpenAI, fake),
        model="gpt-5.6-luna",
        max_output_tokens=180,
    )


@pytest.mark.asyncio
async def test_responses_request_uses_luna_with_no_reasoning() -> None:
    fake = FakeOpenAI(" trubot: Hot ")
    responder = make_responder(fake)

    result = await responder.reply(
        [ConversationMessage(role="user", content="Tim: Yeah its wet")],
        mode=ReplyMode.DIRECT,
        safety_id="safe-user",
    )

    assert result == "Hot"
    assert fake.responses.request is not None
    assert fake.responses.request["model"] == "gpt-5.6-luna"
    assert fake.responses.request["reasoning"] == {"effort": "none"}
    assert fake.responses.request["text"] == {"verbosity": "low"}
    assert fake.responses.request["max_output_tokens"] == 180
    assert fake.responses.request["store"] is False
    assert fake.responses.request["safety_identifier"] == "safe-user"
    assert fake.responses.request["prompt_cache_key"] == "wcb-trubot-personality-v2"
    assert fake.responses.request["input"] == [{"role": "user", "content": "Tim: Yeah its wet"}]
    assert "addressed Trubot directly" in fake.responses.request["instructions"]


@pytest.mark.asyncio
async def test_reaction_focus_is_appended_to_context() -> None:
    fake = FakeOpenAI()
    responder = make_responder(fake)

    await responder.reply(
        [ConversationMessage(role="user", content="Jim: trade offer")],
        mode=ReplyMode.REACTION,
        safety_id="safe-user",
        focus="Jim: Thomas Jones for a third",
    )

    assert fake.responses.request is not None
    assert fake.responses.request["input"][-1] == {
        "role": "user",
        "content": "Reaction target (respond to this):\nJim: Thomas Jones for a third",
    }


@pytest.mark.asyncio
async def test_empty_context_is_rejected_before_an_api_call() -> None:
    fake = FakeOpenAI()
    responder = make_responder(fake)

    with pytest.raises(ResponderError, match="without conversation context"):
        await responder.reply([], mode=ReplyMode.AMBIENT, safety_id="safe-user")
    assert fake.responses.request is None


@pytest.mark.asyncio
async def test_empty_model_output_is_rejected() -> None:
    responder = make_responder(FakeOpenAI("  "))
    with pytest.raises(EmptyResponseError):
        await responder.reply(
            [ConversationMessage(role="user", content="Tim: hello")],
            mode=ReplyMode.DIRECT,
            safety_id="safe-user",
        )


@pytest.mark.asyncio
async def test_close_releases_the_sdk_client() -> None:
    fake = FakeOpenAI()
    responder = make_responder(fake)
    await responder.close()
    assert fake.closed


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("trubot: Hot", "Hot"),
        ("Andrew Truax: Hot", "Hot"),
        ("andrew.truax: Hot", "Hot"),
        ("Truax: Hot", "Hot"),
        ("Hot take: Thomas Jones rules", "Hot take: Thomas Jones rules"),
        (None, ""),
    ],
)
def test_normalize_reply_only_removes_known_speaker_labels(
    raw: str | None,
    expected: str,
) -> None:
    assert normalize_reply(raw) == expected
