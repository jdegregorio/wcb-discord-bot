from datetime import UTC, datetime, timedelta

from trubot.attention import AttentionTracker

START = datetime(2026, 8, 30, 12, tzinfo=UTC)


def test_attention_is_channel_scoped_and_expires_at_the_window_boundary() -> None:
    tracker = AttentionTracker(timedelta(minutes=10))
    tracker.activate(10, START)

    assert tracker.is_active(10, START + timedelta(minutes=9, seconds=59))
    assert not tracker.is_active(11, START + timedelta(minutes=1))
    assert not tracker.is_active(10, START + timedelta(minutes=10))
    assert not tracker.is_active(10, START + timedelta(minutes=11))


def test_reactivation_extends_attention_and_naive_times_are_utc() -> None:
    tracker = AttentionTracker(timedelta(minutes=10))
    tracker.activate(10, START.replace(tzinfo=None))
    tracker.activate(10, START + timedelta(minutes=5))

    assert tracker.is_active(10, START + timedelta(minutes=14))
