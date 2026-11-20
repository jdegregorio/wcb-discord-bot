"""Slow healthy sources must retain full-cohort freshness without quota resets."""

from contextlib import asynccontextmanager
from datetime import timedelta

import pytest
from test_distillation import worker
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.distillation import StudyStore
from trubot.graph import GraphStore
from trubot.learning import LearningStore


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def seed_sources(stores, count):
    for i in range(count):
        stores[0].observe(source(i, content=f"I order caramel dessert after dinner {i}."), now=NOW)
    stores[2].populate(now=NOW)
    return [{"kind": "discord", "message_id": source(i).id} for i in range(count)]


class LogicalDeadlines:
    """Exercise nested allowances without depending on host scheduling latency."""

    def __init__(self):
        self.elapsed = 0
        self.deadlines = []

    @asynccontextmanager
    async def timeout(self, seconds):
        self.deadlines.append(self.elapsed + seconds)
        try:
            yield
        finally:
            self.deadlines.pop()

    def advance(self, seconds):
        self.elapsed += seconds
        if any(self.elapsed >= end for end in self.deadlines):
            raise TimeoutError


def logical_deadlines(monkeypatch):
    clock = LogicalDeadlines()
    monkeypatch.setattr("trubot.distillation.asyncio.timeout", clock.timeout)
    return clock


@pytest.mark.parametrize("count", [2, 6])
async def test_healthy_cohort_can_take_longer_than_one_source_budget(stores, monkeypatch, count):
    refs = seed_sources(stores, count)
    distiller, client, responder, channel = worker(stores)
    clock = logical_deadlines(monkeypatch)
    fetch = channel.fetch_message.side_effect

    async def slow_current(identifier):
        clock.advance(3.2)
        return fetch(identifier)

    channel.fetch_message.side_effect = slow_current
    generate = responder.study_json.side_effect

    async def checked(**kwargs):
        await kwargs["source_check"]()
        return await generate(**kwargs)

    responder.study_json.side_effect = checked
    assert await distiller.cycle(client, episode_refs=refs) == "accepted"
    assert responder.study_json.await_count == 2
    reads = [call.args[0] for call in channel.fetch_message.await_args_list]
    assert reads == [ref["message_id"] for ref in refs] * 4
    assert stores[2].lookup("dessert", guild_id=77, now=NOW)
    assert (
        StudyStore(stores[2])
        .select(now=NOW + timedelta(hours=1), channel_ids=frozenset({10}))
        .reason
        == "paced"
    )
    channel.send.assert_not_awaited()


async def test_one_source_cannot_spend_the_whole_cohort_allowance(stores, monkeypatch, caplog):
    refs = seed_sources(stores, 6)
    distiller, client, responder, channel = worker(stores)
    clock = logical_deadlines(monkeypatch)

    async def stalled(identifier):
        clock.advance(5)

    channel.fetch_message.side_effect = stalled
    assert await distiller.cycle(client, episode_refs=refs) is None
    responder.study_json.assert_not_awaited()
    assert stores[2].status()["nodes"].get("preference", 0) == 0
    assert "reason=timeout" in caplog.text
    assert (
        StudyStore(stores[2])
        .select(now=NOW + timedelta(hours=1), channel_ids=frozenset({10}))
        .reason
        == "paced"
    )
