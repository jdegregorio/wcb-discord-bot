import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from test_context_tools import Provider, response
from test_discord_client import fake_channel, make_client
from test_learning import AUDIT, NOW

from trubot.archives import ArchiveStore
from trubot.budget import UsageLedger
from trubot.context_tools import ContextTools
from trubot.conversation import ConversationImage, ConversationMessage, ReplyMode
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore
from trubot.memory import ContextMemory
from trubot.openai_responder import OpenAITruaxResponder
from trubot.photo_action import PhotoAction
from trubot.reply_diagnostics import log_reply_context
from trubot.up_night import UPNightLocationSkill


@pytest.mark.parametrize("mode", list(ReplyMode))
def test_context_counts_never_log_text_ids_images_or_arbitrary_skill_names(caplog, mode):
    sensitive = "PRIVATE_SENTINEL_987654 https://private.invalid/secret\nforged log entry"
    messages = [
        ConversationMessage("user", sensitive, author_user_id=987654),
        ConversationMessage("assistant", sensitive),
        ConversationMessage("user", sensitive, origin="reference"),
        ConversationMessage("user", sensitive, origin="focus"),
        ConversationMessage(
            "user",
            sensitive,
            origin="memory",
            images=(ConversationImage("data:image/png;base64,SECRET", sensitive),),
        ),
    ]
    with caplog.at_level(logging.INFO, logger="trubot.reply_diagnostics"):
        log_reply_context(
            messages,
            [SimpleNamespace(name=sensitive), UPNightLocationSkill()],
            mode=mode,
            photo_available=True,
            inspection_available=False,
        )
    assert len(caplog.records) == 1
    assert "routes=other,up_location" in caplog.text
    assert "conversation=2 reference=1 focus=1 memory=1 images=1" in caplog.text
    assert "photo=True inspection=False" in caplog.text
    for forbidden in ["PRIVATE", "987654", "https://", "SECRET", "forged", sensitive]:
        assert forbidden not in caplog.text


def test_disabled_diagnostics_do_not_inspect_context():
    class Unreadable:
        def __iter__(self):
            raise AssertionError("disabled tracing inspected context")

    logger = logging.getLogger("trubot.reply_diagnostics")
    old_level = logger.level
    try:
        logger.setLevel(logging.WARNING)
        log_reply_context(
            Unreadable(),
            Unreadable(),
            mode=ReplyMode.DIRECT,
            photo_available=False,
            inspection_available=False,
        )
    finally:
        logger.setLevel(old_level)


async def test_tracing_preserves_exact_provider_request_output_and_accounting(tmp_path, caplog):
    provider = Provider([response("Which location?"), response("Which location?")])
    ledger = UsageLedger(tmp_path / "usage.sqlite3")
    responder = OpenAITruaxResponder(
        provider,
        model="gpt-6-luna",
        max_output_tokens=180,
        budget=ledger,
        context_tools=ContextTools((UPNightLocationSkill(),)),
    )
    messages = [ConversationMessage("user", "PRIVATE_SENTINEL", origin="memory")]
    answers = []
    for level in (logging.INFO, logging.WARNING):
        with caplog.at_level(level, logger="trubot.reply_diagnostics"):
            answers.append(
                await responder.reply(
                    messages,
                    mode=ReplyMode.DIRECT,
                    safety_id="synthetic",
                    target="Casey: How were sky conditions last night?",
                    photo_action=PhotoAction(AsyncMock()),
                )
            )
    assert answers == ["Which location?", "Which location?"]
    assert provider.requests[0] == provider.requests[1]
    assert "PRIVATE_SENTINEL" in str(provider.requests[0])
    assert "show_source_photo" in str(provider.requests[0])
    assert "PRIVATE_SENTINEL" not in caplog.text
    assert caplog.text.count("routes=up_location") == 1
    assert ledger.summary()["attempts"] == 2
    assert ledger.summary()["unsettled_attempts"] == 0


@pytest.mark.parametrize(
    "state", ["unavailable", "identity_unverified", "scope_denied", "assembled"]
)
async def test_memory_trace_distinguishes_real_verification_and_assembly_states(
    tmp_path, caplog, state
):
    client, _, _, _ = make_client(clock=lambda: NOW)
    channel = fake_channel()
    if state != "unavailable":
        store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
        archive = ArchiveStore.initialize(store)
        archive.import_document(
            b"legacy.target\n  8:00 AM\nPRIVATE_SENTINEL baseball.",
            channel="general",
            target_alias="legacy.target",
            alias_basis="Synthetic audit",
            origin={"kind": "synthetic"},
            now=NOW,
        )
        learner = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
        learner.verified = state != "identity_unverified"
        client._learning, client._memory = learner, ContextMemory(store)
        if state == "scope_denied":
            channel.guild.id = 999
    with caplog.at_level(logging.INFO, logger="trubot.discord_client"):
        result = await client._memory_context(channel, "Casey: baseball", [])
    assert f"Reply memory state={state}" in caplog.text
    assert "PRIVATE_SENTINEL" not in caplog.text
    if state == "assembled":
        assert result
        assert "candidates=1 verified=1 native_contexts=0" in caplog.text
    else:
        assert result == ""
    await client.close()
