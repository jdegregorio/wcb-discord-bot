"""Small answers should not pay for cosmetic novelty; source checks still apply."""

from unittest.mock import AsyncMock

import pytest
from test_response_repetition import SequenceAPI, history, responder

from trubot.conversation import ConversationMessage, ReplyMode
from trubot.openai_responder import _stale_bot_echo


@pytest.mark.parametrize("mode", [ReplyMode.DIRECT, ReplyMode.FOLLOW_UP, ReplyMode.REACTION])
@pytest.mark.parametrize(
    "draft",
    [
        "The fictional Harbor Otters.",
        "A moderately official snack commissioner.",
        "They're the fictional Harbor Otters.",
        "They\u2019re the fictional Harbor Otters.",
        "Otters. Harbor Otters!!!",
    ],
)
async def test_small_echo_needs_no_cosmetic_source_recheck_or_second_attempt(
    mode, draft, monkeypatch
):
    api = SequenceAPI(draft, "An unnecessary rewrite.")
    r, ledger = responder(api, monkeypatch)
    check = AsyncMock(return_value=True)
    messages = [
        *history(draft),
        ConversationMessage("user", "Invented current source evidence.", origin="memory"),
    ]
    assert (
        await r.reply(
            messages,
            mode=mode,
            safety_id="test",
            target="Casey: Which fictional team was it?",
            refresh_check=check,
        )
        == draft
    )
    check.assert_not_awaited()
    assert len(api.requests) == ledger.summary()["attempts"] == 1


@pytest.mark.parametrize(
    "draft",
    [
        "The fictional Harbor Otters win again.",  # Six words retain exact-echo recovery.
        "Extraordinarily incomprehensibly bureaucratically administered snacks.",
    ],
)
def test_more_words_or_long_tokens_remain_substantial(draft):
    assert _stale_bot_echo(draft, history(draft), "Casey: New fictional setup.")


async def test_short_three_sentence_echo_still_receives_brevity_repair(monkeypatch):
    draft = "Congratulations. Absolutely wonderful. Great work."
    api = SequenceAPI(draft, "Congratulations on that achievement!")
    r, ledger = responder(api, monkeypatch)
    check = AsyncMock(return_value=True)
    answer = await r.reply(
        history(draft),
        mode=ReplyMode.DIRECT,
        safety_id="test",
        target="Casey: I finished my first race.",
        refresh_check=check,
    )
    assert answer == "Congratulations on that achievement!"
    check.assert_awaited_once_with()
    assert len(api.requests) == ledger.summary()["attempts"] == 2
    assert "exceeded" in api.requests[1]["instructions"]
    assert "copied wording" not in api.requests[1]["instructions"]


async def test_short_continuity_does_not_reclassify_unknown_facts_as_supported(monkeypatch):
    draft = "I don't know that detail."
    api = SequenceAPI(draft)
    r, ledger = responder(api, monkeypatch)
    assert (
        await r.reply(
            history(draft),
            mode=ReplyMode.DIRECT,
            safety_id="test",
            target="Casey: What was an unspecified person's first pet?",
        )
        == draft
    )
    assert len(api.requests) == ledger.summary()["attempts"] == 1
