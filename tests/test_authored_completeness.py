"""A retained authored passage must not silently lose its closing qualification."""

import json

import pytest
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.learning import LearningStore, LearningUnavailable
from trubot.memory import ContextMemory, MemoryCandidate

CLOSING = "This proposal is fictional. I oppose replacing kickers; keep kickers."
QUALIFIED = "Replace kickers with a mascot slot. " + "Logistics remain undecided. " * 60 + CLOSING


def archived(tmp_path, body):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    archive = ArchiveStore.initialize(store)
    archive.import_document(
        (
            "peer\n  8:00 AM\nI support replacing kickers.\nfixture.target\n  8:01 AM\n" + body
        ).encode(),
        channel="invented",
        target_alias="fixture.target",
        alias_basis="Invented completeness regression",
        origin={"kind": "synthetic"},
        now=NOW,
    )
    return store, archive, ContextMemory(store)


@pytest.mark.parametrize("native", [False, True])
def test_complete_stored_authored_qualification_reaches_reply_packet(tmp_path, native):
    store, _, memory = archived(tmp_path, "Other topic.")
    if native:
        store.observe(source(content=QUALIFIED), now=NOW)
    else:
        _, _, memory = archived(tmp_path / "second", QUALIFIED)
    selected = memory.candidates("mascot kickers", guild_id=77, now=NOW)
    packet = memory.render(selected, request="What did Andrew say about kickers?", now=NOW)
    assert 1500 < len(QUALIFIED) < 4000
    assert QUALIFIED in packet
    assert CLOSING in packet


@pytest.mark.parametrize("body", ["x" * 6000, "🦆" * 1500], ids=["ascii", "unicode"])
def test_exact_authored_byte_limit_keeps_complete_text(tmp_path, body):
    _, _, memory = archived(tmp_path, "mascot " + body[7:])
    # Separate character and byte limits, including a multibyte closing marker.
    with memory.archives._transaction() as db:
        db.execute("UPDATE messages SET content=? WHERE target=1", (body,))
    # A literal source lookup avoids relying on lexical matches in boundary strings.
    with memory.archives._transaction() as db:
        row = db.execute("SELECT document, ordinal FROM messages WHERE target=1").fetchone()
    selected = [MemoryCandidate({"kind": "slack", **dict(row)}, body, 1)]
    packet = memory.render(selected, now=NOW)
    assert json.loads(packet.split("\n", 1)[1])[0]["text"] == body


@pytest.mark.parametrize(
    "body", ["private-prefix " + "x" * 6000, "🦆" * 1501], ids=["ascii", "unicode"]
)
def test_oversized_authored_passage_is_wholly_omitted_without_peer_standin(tmp_path, body):
    store, archive, memory = archived(tmp_path, "mascot " + body)
    selected = memory.candidates("mascot", guild_id=77, now=NOW)
    packet = memory.render_packet(selected, now=NOW)
    item = json.loads(packet.text.split("\n", 1)[1])[0]
    assert item["text"] == ""
    assert "source_gap" in item
    assert body[:100] not in packet.text
    assert "I support replacing kickers." not in packet.text
    assert not packet.allow_voice_examples
    archive.remove_document(selected[0].source["document"], now=NOW)
    assert memory.render(selected, now=NOW) == ""
    store.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        memory.render(selected, now=NOW)


def test_complete_source_revalidation_and_quotation_never_use_a_prefix(tmp_path):
    store, _, memory = archived(tmp_path, "Other topic.")
    store.observe(source(content=QUALIFIED), now=NOW)
    selected = memory.candidates("mascot", guild_id=77, now=NOW, quotation=CLOSING)
    assert CLOSING in memory.render(selected, now=NOW, quotation=CLOSING)
    store.invalidate(10, [source().id], deleted=False, now=NOW)
    store.observe(source(content="I changed my vote.", authoritative=True), now=NOW)
    assert not memory.render(selected, now=NOW, quotation=CLOSING)
    assert "I changed my vote." in memory.render(selected, now=NOW)
    store.invalidate(10, [source().id], deleted=True, now=NOW)
    assert not memory.render(selected, now=NOW)


def test_oversized_source_cannot_supply_a_short_matching_quote(tmp_path):
    _, _, memory = archived(tmp_path, "mascot " + "x" * 6000)
    selected = memory.candidates("mascot", guild_id=77, now=NOW, quotation="mascot")
    assert selected
    packet = memory.render_packet(selected, quotation="mascot", now=NOW)
    assert packet.text == ""
    assert not packet.allow_voice_examples


def test_mixed_packet_keeps_other_complete_sources_and_their_context(tmp_path):
    store, _, memory = archived(tmp_path, "mascot " + "x" * 6000)
    store.observe(source(content="Keep kickers, not mascots."), now=NOW)
    selected = memory.candidates("mascot kickers", guild_id=77, now=NOW)
    packet = memory.render_packet(selected, now=NOW)
    data = json.loads(packet.text.split("\n", 1)[1])
    assert len(data) == 2
    assert {r["text"] for r in data} == {"", "Keep kickers, not mascots."}
    assert packet.allow_voice_examples
    assert "I support replacing kickers." not in packet.text


def test_oversized_native_source_loses_context_and_retains_explicit_gap(tmp_path):
    from trubot.native_context import NativeEpisode

    store, _, memory = archived(tmp_path, "Unrelated topic.")
    text = "mascot " + "🦆" * 1500
    store.observe(source(content=text), now=NOW)
    selected = memory.candidates("mascot", guild_id=77, now=NOW)
    episode = NativeEpisode(text, None, ({"author": "peer", "text": "I vote yes."},))
    packet = memory.render_packet(selected, native_episodes={source().id: episode}, now=NOW)
    data = json.loads(packet.text.split("\n", 1)[1])[0]
    assert data["text"] == "" and data["source_gap"]
    assert "I vote yes." not in packet.text
    assert not packet.allow_voice_examples
    store.observe(source(content="No mascots.", authoritative=True), now=NOW)
    packet = memory.render_packet(selected, native_episodes={source().id: episode}, now=NOW)
    assert "No mascots." in packet.text
    assert "I vote yes." not in packet.text
    assert packet.allow_voice_examples
