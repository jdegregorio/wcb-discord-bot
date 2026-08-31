"""Pure policy for Trubot's restrained, ambient channel participation."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from enum import StrEnum


class SchedulingAction(StrEnum):
    SCHEDULE = "schedule"
    CANCEL = "cancel"


@dataclass(frozen=True, slots=True)
class ParticipationPolicy:
    delay: timedelta
    activity_window: timedelta
    min_interval: timedelta
    daily_limit: int
    min_participants: int


@dataclass(frozen=True, slots=True)
class Observation:
    action: SchedulingAction
    revision: int


@dataclass(frozen=True, slots=True)
class AmbientEligibility:
    requester_user_id: int


@dataclass(frozen=True, slots=True)
class ParticipationSnapshot:
    recent_participants: int
    ambient_replies_today: int
    last_reply_at: datetime | None
    revision: int


@dataclass(frozen=True, slots=True)
class _Activity:
    occurred_at: datetime
    user_id: int


@dataclass(slots=True)
class _ChannelState:
    recent: deque[_Activity] = field(default_factory=deque)
    revision: int = 0
    last_reply_at: datetime | None = None
    count_date: date | None = None
    ambient_replies_today: int = 0


class ParticipationTracker:
    def __init__(self, policy: ParticipationPolicy) -> None:
        self.policy = policy
        self._channels: dict[int, _ChannelState] = {}

    def observe(
        self,
        channel_id: int,
        user_id: int,
        occurred_at: datetime,
        *,
        allow_ambient: bool,
    ) -> Observation:
        now = _as_utc(occurred_at)
        state = self._state(channel_id)
        state.revision += 1
        self._roll_day(state, now)
        state.recent.append(_Activity(now, user_id))
        self._trim(state, now)

        action = (
            SchedulingAction.SCHEDULE
            if allow_ambient and self._eligible(state, now)
            else SchedulingAction.CANCEL
        )
        return Observation(action=action, revision=state.revision)

    def ambient_eligibility(
        self,
        channel_id: int,
        revision: int,
        at: datetime,
    ) -> AmbientEligibility | None:
        now = _as_utc(at)
        state = self._state(channel_id)
        self._roll_day(state, now)
        self._trim(state, now)
        if state.revision != revision or not self._eligible(state, now):
            return None
        return AmbientEligibility(requester_user_id=state.recent[-1].user_id)

    def invalidate(self, channel_id: int) -> None:
        self._state(channel_id).revision += 1

    def record_reply(self, channel_id: int, at: datetime, *, ambient: bool) -> None:
        now = _as_utc(at)
        state = self._state(channel_id)
        self._roll_day(state, now)
        state.last_reply_at = now
        state.revision += 1
        if ambient:
            state.ambient_replies_today += 1

    def snapshot(self, channel_id: int, at: datetime) -> ParticipationSnapshot:
        now = _as_utc(at)
        state = self._state(channel_id)
        self._roll_day(state, now)
        self._trim(state, now)
        return ParticipationSnapshot(
            recent_participants=len({activity.user_id for activity in state.recent}),
            ambient_replies_today=state.ambient_replies_today,
            last_reply_at=state.last_reply_at,
            revision=state.revision,
        )

    def _state(self, channel_id: int) -> _ChannelState:
        return self._channels.setdefault(channel_id, _ChannelState())

    def _eligible(self, state: _ChannelState, now: datetime) -> bool:
        if self.policy.daily_limit == 0:
            return False
        if state.ambient_replies_today >= self.policy.daily_limit:
            return False
        participants = {activity.user_id for activity in state.recent}
        if len(participants) < self.policy.min_participants:
            return False
        return not (
            state.last_reply_at is not None and now - state.last_reply_at < self.policy.min_interval
        )

    def _trim(self, state: _ChannelState, now: datetime) -> None:
        cutoff = now - self.policy.activity_window
        while state.recent and state.recent[0].occurred_at < cutoff:
            state.recent.popleft()

    @staticmethod
    def _roll_day(state: _ChannelState, now: datetime) -> None:
        if state.count_date != now.date():
            state.count_date = now.date()
            state.ambient_replies_today = 0


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
