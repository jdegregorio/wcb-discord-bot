"""Short-lived per-channel attention after Trubot is explicitly addressed."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta


class AttentionTracker:
    def __init__(self, window: timedelta) -> None:
        self.window = window
        self._active_until: dict[int, datetime] = {}

    def activate(self, channel_id: int, at: datetime) -> None:
        self._active_until[channel_id] = _as_utc(at) + self.window

    def is_active(self, channel_id: int, at: datetime) -> bool:
        now = _as_utc(at)
        active_until = self._active_until.get(channel_id)
        if active_until is None:
            return False
        if now >= active_until:
            self._active_until.pop(channel_id, None)
            return False
        return True


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
