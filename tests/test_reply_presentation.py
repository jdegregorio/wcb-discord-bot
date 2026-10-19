"""Synthetic dialogue framing must not change source artifacts or evade reply checks."""

from unittest.mock import AsyncMock

import pytest
from test_response_repetition import NEW, OLD, SequenceAPI, history, responder

from trubot.conversation import ConversationMessage, ReplyMode
from trubot.openai_responder import normalize_reply
from trubot.reply_brevity import needs_brief_reply, sentence_count

TARGET = "Casey: In a fictional fantasy matchup we both scored badly. Your reply?"
LONG = "A glorious disaster. We both lost to the waiver wire. I still want a banner."
SHORT = "I still want a banner for this glorious disaster."


@pytest.mark.parametrize("quotes", [('"', '"'), ("“", "”")])
@pytest.mark.parametrize("prefix", ["", "Trubot: "])
def test_ordinary_dialogue_is_spoken_directly(quotes, prefix):
    raw = prefix + quotes[0] + "That's a spectacularly bad roster." + quotes[1]
    assert normalize_reply(raw, target=TARGET) == "That's a spectacularly bad roster."


@pytest.mark.parametrize(
    "target",
    [
        "Casey: Quote your reply.",
        "Casey: Repeat that verbatim.",
        "Casey: Give the exact wording.",
        "Casey: What did you say when you posted it?",
        "Casey: What was the original caption for that photo? Text only.",
        "Casey: Write a caption for this invented picture.",
        None,
        "",
    ],
)
async def test_requested_artifacts_and_unfocused_text_retain_quotes(target, monkeypatch):
    raw = '"' + LONG + '"'
    api = SequenceAPI(raw)
    r, ledger = responder(api, monkeypatch)
    assert (
        await r.reply(
            [ConversationMessage("user", "Invented ambient context")],
            mode=ReplyMode.DIRECT,
            safety_id="test",
            target=target,
        )
        == raw
    )
    assert len(api.requests) == ledger.summary()["attempts"] == 1


@pytest.mark.parametrize(
    "text",
    [
        'He said "not great". Fair assessment.',
        '"One quotation." "Another quotation."',
        "“One quotation.” “Another quotation.”",
        '"Unfinished quotation.',
        '“Mismatched ending."',
        "'Single apostrophe framing stays intact.'",
        "“He said “not great”.”",
    ],
)
def test_embedded_multiple_and_ambiguous_quotations_are_preserved(text):
    assert normalize_reply(text, target=TARGET) == text


@pytest.mark.parametrize("quotes", [('"', '"'), ("“", "”")])
@pytest.mark.parametrize("mode", [ReplyMode.DIRECT, ReplyMode.REACTION, ReplyMode.FOLLOW_UP])
async def test_whole_wrapper_cannot_bypass_the_existing_shared_repair(mode, quotes, monkeypatch):
    raw = quotes[0] + LONG + quotes[1]
    assert sentence_count(raw) == 3
    assert needs_brief_reply(raw, [], TARGET)
    api = SequenceAPI(raw, quotes[0] + SHORT + quotes[1])
    r, ledger = responder(api, monkeypatch)
    assert await r.reply([], mode=mode, safety_id="test", target=TARGET) == SHORT
    assert len(api.requests) == ledger.summary()["attempts"] == 2
    assert api.requests[1]["input"][:-2] == api.requests[0]["input"]
    assert api.requests[1]["input"][-2] == {"role": "assistant", "content": LONG}
    assert TARGET in api.requests[1]["input"][-1]["content"]
    assert api.requests[1]["store"] is False


@pytest.mark.parametrize("current", [False, True])
async def test_wrapped_draft_repair_preserves_private_source_refresh(current, monkeypatch):
    api = SequenceAPI('"' + LONG + '"', '"' + SHORT + '"')
    r, ledger = responder(api, monkeypatch)
    check = AsyncMock(return_value=current)
    assert await r.reply(
        [ConversationMessage("user", "Invented evidence", origin="memory")],
        mode=ReplyMode.DIRECT,
        safety_id="test",
        target=TARGET,
        refresh_check=check,
    ) == (SHORT if current else LONG)
    check.assert_awaited_once_with()
    assert len(api.requests) == ledger.summary()["attempts"] == (2 if current else 1)


async def test_still_wrapped_overlong_repair_never_earns_a_third_attempt(monkeypatch):
    api = SequenceAPI('"' + LONG + '"', '"' + LONG + '"')
    r, ledger = responder(api, monkeypatch)
    assert await r.reply([], mode=ReplyMode.DIRECT, safety_id="test", target=TARGET) == LONG
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_dialogue_framing_cannot_hide_recipient_abstention(monkeypatch):
    api = SequenceAPI('"<NO_REPLY>"')
    r, ledger = responder(api, monkeypatch)
    assert await r.reply([], mode=ReplyMode.FOLLOW_UP, safety_id="test", target=TARGET) is None
    assert len(api.requests) == ledger.summary()["attempts"] == 1


async def test_framing_change_does_not_hide_an_older_bot_echo(monkeypatch):
    messages = history()
    messages[1] = ConversationMessage("assistant", '"' + OLD + '"')
    api = SequenceAPI(OLD, '"' + NEW + '"')
    r, ledger = responder(api, monkeypatch)
    assert await r.reply(messages, mode=ReplyMode.DIRECT, safety_id="test", target=TARGET) == NEW
    assert len(api.requests) == ledger.summary()["attempts"] == 2


def test_embedded_source_punctuation_stays_inside_its_quotation():
    assert sentence_count('He wrote "One. Two. Three.". That is the entire excerpt.') == 2
