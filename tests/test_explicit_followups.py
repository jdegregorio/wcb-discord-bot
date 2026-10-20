from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from test_context_tools import Provider, call, response

from trubot.budget import UsageLedger
from trubot.context_tools import ContextTools, ToolProtocolError
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.openai_responder import OpenAITruaxResponder
from trubot.up_conditions import UPConditionsSkill
from trubot.up_night import UPNightLocationSkill, UPNightSkill


@pytest.mark.parametrize(
    "question,name",
    [
        ("And check current Munising sky conditions now?", UPConditionsSkill.name),
        ("And how were Marquette sky conditions last night?", UPNightSkill.name),
        ("How were sky conditions last night?", UPNightLocationSkill.name),
    ],
)
def test_complete_followup_selects_only_its_existing_skill(question: str, name: str) -> None:
    tools = ContextTools((UPConditionsSkill(), UPNightSkill(), UPNightLocationSkill()))
    selected = tools.select(question, ReplyMode.FOLLOW_UP)
    assert [s.name for s in selected] == [name]


def test_ambiguous_location_followup_does_not_inherit_a_tool() -> None:
    tools = ContextTools((UPConditionsSkill(), UPNightSkill(), UPNightLocationSkill()))
    assert tools.select("What about Munising?", ReplyMode.FOLLOW_UP) == ()
    assert tools.select("Munising.", ReplyMode.FOLLOW_UP) == ()


@pytest.mark.parametrize("night", [False, True])
async def test_followup_reads_once_and_accounts_both_turns(tmp_path: Path, night: bool) -> None:
    skill = UPNightSkill() if night else UPConditionsSkill()
    question = (
        "Casey: And how were Marquette sky conditions last night?"
        if night
        else "Casey: And check current Munising sky conditions now?"
    )
    provider = Provider(
        [response(calls=[call(name=skill.name)]), response("The report is overcast.")]
    )
    ledger = UsageLedger(tmp_path / "usage.sqlite3")
    responder = OpenAITruaxResponder(
        provider,  # type: ignore[arg-type]
        model="gpt-6-luna",
        max_output_tokens=512,
        budget=ledger,
        context_tools=ContextTools((skill,)),
    )
    source_check = AsyncMock(return_value=True)
    with patch.object(skill, "read", new_callable=AsyncMock, return_value={"fresh": True}) as read:
        reply = await responder.reply(
            [ConversationMessage("assistant", "An earlier report is stale.")],
            mode=ReplyMode.FOLLOW_UP,
            target=question,
            safety_id="synthetic",
            refresh_check=source_check,
        )
    assert reply == "The report is overcast."
    read.assert_awaited_once()
    assert len(provider.requests) == 2
    assert ledger.summary()["attempts"] == 2
    assert provider.requests[0]["reasoning"] == {"effort": "low"}
    assert provider.requests[-1]["tool_choice"] == "none"
    assert "tools" not in provider.requests[-1]
    assert source_check.await_count == 2


async def test_followup_recipient_abstention_does_not_execute_available_read(
    tmp_path: Path,
) -> None:
    skill = UPConditionsSkill()
    provider = Provider([response("<NO_REPLY>")])
    responder = OpenAITruaxResponder(
        provider,  # type: ignore[arg-type]
        model="gpt-6-luna",
        max_output_tokens=512,
        budget=UsageLedger(tmp_path / "usage.sqlite3"),
        context_tools=ContextTools((skill,)),
    )
    with patch.object(skill, "read", new_callable=AsyncMock) as read:
        assert (
            await responder.reply(
                [ConversationMessage("assistant", "Marquette was cloudy.")],
                mode=ReplyMode.FOLLOW_UP,
                target="Casey: Lee, check current Munising sky conditions now?",
                safety_id="synthetic",
            )
            is None
        )
    read.assert_not_awaited()
    assert len(provider.requests) == 1
    assert provider.requests[0]["tools"]


async def test_followup_changed_source_blocks_public_read(tmp_path: Path) -> None:
    skill = UPConditionsSkill()
    provider = Provider([response(calls=[call()])])
    responder = OpenAITruaxResponder(
        provider,  # type: ignore[arg-type]
        model="gpt-6-luna",
        max_output_tokens=512,
        budget=UsageLedger(tmp_path / "usage.sqlite3"),
        context_tools=ContextTools((skill,)),
    )
    with (
        patch.object(skill, "read", new_callable=AsyncMock) as read,
        pytest.raises(ToolProtocolError, match="changed"),
    ):
        await responder.reply(
            [ConversationMessage("assistant", "Earlier source context.")],
            mode=ReplyMode.FOLLOW_UP,
            target="Casey: Check current Munising sky conditions now?",
            safety_id="synthetic",
            refresh_check=AsyncMock(return_value=False),
        )
    read.assert_not_awaited()
    assert len(provider.requests) == 1
