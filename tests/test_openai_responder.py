import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from openai import AsyncOpenAI

from trubot.budget import UsageLedger
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
        return SimpleNamespace(
            output_text=self.output_text,
            usage=SimpleNamespace(
                input_tokens=1000,
                input_tokens_details=SimpleNamespace(cached_tokens=800),
                output_tokens=10,
            ),
        )


class FakeOpenAI:
    def __init__(self, output_text: str | None = "Hot") -> None:
        self.responses = FakeResponses(output_text)
        self.closed = False

    def with_options(self, **_kwargs: object) -> "FakeOpenAI":
        return self

    async def close(self) -> None:
        self.closed = True


def make_responder(fake: FakeOpenAI) -> OpenAITruaxResponder:
    return OpenAITruaxResponder(
        cast(AsyncOpenAI, fake),
        model="gpt-6-luna",
        max_output_tokens=180,
        budget=UsageLedger(Path(os.environ["TRUBOT_USAGE_LEDGER_PATH"])),
    )


@pytest.mark.asyncio
async def test_explicit_responses_use_luna_without_reasoning() -> None:
    fake = FakeOpenAI(" trubot: Hot ")
    responder = make_responder(fake)

    result = await responder.reply(
        [ConversationMessage(role="user", content="Tim: Yeah its wet")],
        mode=ReplyMode.DIRECT,
        safety_id="safe-user",
        target="Tim: Yeah its wet",
    )

    assert result == "Hot"
    assert fake.responses.request is not None
    assert fake.responses.request["model"] == "gpt-6-luna"
    assert fake.responses.request["service_tier"] == "default"
    assert fake.responses.request["reasoning"] == {"effort": "none"}
    assert fake.responses.request["text"] == {"verbosity": "low"}
    assert fake.responses.request["max_output_tokens"] == 180
    assert fake.responses.request["store"] is False
    assert fake.responses.request["safety_identifier"] == "safe-user"
    assert fake.responses.request["prompt_cache_key"] == "wcb-trubot-personality-v7"
    assert fake.responses.request["input"] == [
        {
            "role": "user",
            "content": (
                "CURRENT MESSAGE - answer this now; earlier messages are context only:\n"
                "Tim: Yeah its wet"
            ),
        }
    ]
    assert "addressed Trubot directly" in fake.responses.request["instructions"]


@pytest.mark.asyncio
async def test_reaction_target_is_appended_to_context() -> None:
    fake = FakeOpenAI()
    responder = make_responder(fake)

    await responder.reply(
        [ConversationMessage(role="user", content="Jim: trade offer")],
        mode=ReplyMode.REACTION,
        safety_id="safe-user",
        target="Jim: Thomas Jones for a third",
    )

    assert fake.responses.request is not None
    assert fake.responses.request["input"][-1] == {
        "role": "user",
        "content": (
            "REACTION TARGET - answer this now; earlier messages are context only:\n"
            "Jim: Thomas Jones for a third"
        ),
    }


@pytest.mark.asyncio
async def test_follow_up_candidate_can_abstain() -> None:
    fake = FakeOpenAI(" <NO_REPLY> ")
    responder = make_responder(fake)

    result = await responder.reply(
        [ConversationMessage(role="assistant", content="Hot")],
        mode=ReplyMode.FOLLOW_UP,
        safety_id="safe-user",
        target="Jim: Tim, are you making that trade?",
    )

    assert result is None
    assert fake.responses.request is not None
    assert fake.responses.request["input"][-1] == {
        "role": "user",
        "content": (
            "LATEST MESSAGE - decide whether this is addressed to Trubot; "
            "answer or abstain as instructed:\nJim: Tim, are you making that trade?"
        ),
    }
    assert "return exactly <NO_REPLY>" in fake.responses.request["instructions"]


@pytest.mark.asyncio
async def test_follow_up_candidate_can_generate_a_reply() -> None:
    responder = make_responder(FakeOpenAI("Obviously Thomas Jones."))

    result = await responder.reply(
        [ConversationMessage(role="assistant", content="Hot")],
        mode=ReplyMode.FOLLOW_UP,
        safety_id="safe-user",
        target="Jim: Then who is your favorite player?",
    )

    assert result == "Obviously Thomas Jones."


@pytest.mark.asyncio
async def test_direct_target_replaces_latest_message_after_bad_assistant_history() -> None:
    fake = FakeOpenAI()
    responder = make_responder(fake)
    latest = 'Joe: @trubot what are you talking about "response". Who is your favorite player?'
    history = [
        ConversationMessage(role="user", content="Joe: @trubot what is your mom like?"),
        ConversationMessage(
            role="assistant",
            content="Joe, you have misspelled respond enough times.",
        ),
        ConversationMessage(role="user", content="Joe: @trubot what do you mean?"),
        ConversationMessage(
            role="assistant",
            content="Joe, you have misspelled respond again.",
        ),
        ConversationMessage(role="user", content=latest),
    ]

    await responder.reply(
        history,
        mode=ReplyMode.DIRECT,
        safety_id="safe-user",
        target=latest,
    )

    assert fake.responses.request is not None
    model_input = fake.responses.request["input"]
    assert len(model_input) == len(history)
    assert model_input[-1] == {
        "role": "user",
        "content": (
            "CURRENT MESSAGE - answer this now; earlier messages are context only:\n" + latest
        ),
    }
    assert "Earlier Trubot replies are fallible" in fake.responses.request["instructions"]


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


@pytest.mark.parametrize(
    ("mode", "effort", "ceiling"),
    [
        (ReplyMode.DIRECT, "none", 180),
        (ReplyMode.REACTION, "none", 180),
        (ReplyMode.AMBIENT, "none", 180),
        (ReplyMode.FOLLOW_UP, "low", 512),
    ],
)
@pytest.mark.asyncio
async def test_only_inferred_followups_receive_the_contextual_reasoning_budget(
    mode: ReplyMode,
    effort: str,
    ceiling: int,
) -> None:
    fake = FakeOpenAI("Hot")
    responder = OpenAITruaxResponder(
        cast(AsyncOpenAI, fake),
        model="gpt-6-luna",
        max_output_tokens=512,
        budget=UsageLedger(Path(os.environ["TRUBOT_USAGE_LEDGER_PATH"])),
    )
    await responder.reply(
        [ConversationMessage(role="user", content="Casey: Good game")],
        mode=mode,
        safety_id="synthetic-user",
    )
    assert fake.responses.request["reasoning"] == {"effort": effort}
    assert fake.responses.request["max_output_tokens"] == ceiling


@pytest.mark.parametrize("mode", [ReplyMode.DIRECT, ReplyMode.REACTION, ReplyMode.FOLLOW_UP])
@pytest.mark.asyncio
async def test_target_retains_pixels_and_reserves_images_before_provider_call(
    mode, private_test_ledger
):
    from trubot.conversation import ConversationImage
    from trubot.vision import IMAGE_TOKEN_BOUND

    fake = FakeOpenAI("A red square.")
    responder = make_responder(fake)
    image = ConversationImage("data:image/jpeg;base64,synthetic", "Synthetic pixels")
    await responder.reply(
        [ConversationMessage("user", "Joe: What is this?", (image,))],
        mode=mode,
        safety_id="synthetic",
        target="Joe: What is this?",
    )
    parts = fake.responses.request["input"][-1]["content"]
    assert len(fake.responses.request["input"]) == 1
    assert parts[-1]["type"] == "input_image"
    assert parts[-1]["image_url"] == image.data_url
    assert parts[-1]["detail"] == "high"
    with private_test_ledger._transaction() as db:
        row = db.execute("SELECT * FROM attempts").fetchone()
        assert row["reserved"] > IMAGE_TOKEN_BOUND * 125


@pytest.mark.asyncio
async def test_excess_images_are_rejected_before_provider_call():
    from trubot.conversation import ConversationImage

    fake = FakeOpenAI()
    responder = make_responder(fake)
    image = ConversationImage("data:image/jpeg;base64,synthetic", "Synthetic")
    with pytest.raises(ResponderError, match="Too many"):
        await responder.reply(
            [ConversationMessage("user", "test", (image, image, image))],
            mode=ReplyMode.DIRECT,
            safety_id="synthetic",
        )
    assert fake.responses.request is None
