from datetime import UTC, datetime, timedelta

from trubot.participation import (
    ParticipationPolicy,
    ParticipationTracker,
    SchedulingAction,
)

START = datetime(2026, 8, 30, 12, tzinfo=UTC)


def tracker(
    *,
    window: timedelta = timedelta(hours=1),
    interval: timedelta = timedelta(hours=2),
    limit: int = 3,
) -> ParticipationTracker:
    return ParticipationTracker(
        ParticipationPolicy(
            delay=timedelta(minutes=10),
            activity_window=window,
            min_interval=interval,
            daily_limit=limit,
            min_participants=2,
        )
    )


def test_two_recent_people_schedule_an_ambient_reply() -> None:
    subject = tracker()

    first = subject.observe(10, 1, START, allow_ambient=True)
    second = subject.observe(10, 2, START + timedelta(minutes=1), allow_ambient=True)

    assert first.action is SchedulingAction.CANCEL
    assert second.action is SchedulingAction.SCHEDULE
    eligibility = subject.ambient_eligibility(10, second.revision, START + timedelta(minutes=11))
    assert eligibility is not None
    assert eligibility.requester_user_id == 2


def test_new_activity_invalidates_an_old_quiet_period() -> None:
    subject = tracker()
    subject.observe(10, 1, START, allow_ambient=True)
    scheduled = subject.observe(10, 2, START + timedelta(minutes=1), allow_ambient=True)
    replacement = subject.observe(10, 1, START + timedelta(minutes=2), allow_ambient=True)

    assert replacement.action is SchedulingAction.SCHEDULE
    assert (
        subject.ambient_eligibility(10, scheduled.revision, START + timedelta(minutes=12)) is None
    )
    assert subject.ambient_eligibility(10, replacement.revision, START + timedelta(minutes=12))


def test_direct_trigger_cancels_ambient_scheduling() -> None:
    subject = tracker()
    subject.observe(10, 1, START, allow_ambient=True)
    direct = subject.observe(10, 2, START + timedelta(minutes=1), allow_ambient=False)

    assert direct.action is SchedulingAction.CANCEL
    assert subject.ambient_eligibility(10, direct.revision, START + timedelta(minutes=11))


def test_any_successful_reply_starts_the_ambient_cooldown() -> None:
    subject = tracker()
    subject.observe(10, 1, START, allow_ambient=True)
    subject.observe(10, 2, START, allow_ambient=True)
    subject.record_reply(10, START, ambient=False)

    blocked = subject.observe(10, 1, START + timedelta(hours=1), allow_ambient=True)
    allowed = subject.observe(10, 2, START + timedelta(hours=2), allow_ambient=True)

    assert blocked.action is SchedulingAction.CANCEL
    assert allowed.action is SchedulingAction.SCHEDULE


def test_daily_limit_resets_at_the_next_utc_day() -> None:
    subject = tracker(interval=timedelta(0), limit=1)
    subject.observe(10, 1, START, allow_ambient=True)
    subject.observe(10, 2, START, allow_ambient=True)
    subject.record_reply(10, START, ambient=True)

    blocked = subject.observe(10, 1, START + timedelta(minutes=1), allow_ambient=True)
    subject.observe(10, 1, START + timedelta(days=1), allow_ambient=True)
    next_day = subject.observe(10, 2, START + timedelta(days=1), allow_ambient=True)

    assert blocked.action is SchedulingAction.CANCEL
    assert next_day.action is SchedulingAction.SCHEDULE
    assert subject.snapshot(10, START + timedelta(days=1)).ambient_replies_today == 0


def test_activity_outside_the_window_is_trimmed() -> None:
    subject = tracker(window=timedelta(minutes=30))
    subject.observe(10, 1, START, allow_ambient=True)
    later = subject.observe(10, 2, START + timedelta(minutes=31), allow_ambient=True)

    assert later.action is SchedulingAction.CANCEL
    assert subject.snapshot(10, START + timedelta(minutes=31)).recent_participants == 1


def test_zero_daily_limit_disables_ambient_replies() -> None:
    subject = tracker(limit=0)
    subject.observe(10, 1, START, allow_ambient=True)
    observation = subject.observe(10, 2, START, allow_ambient=True)
    assert observation.action is SchedulingAction.CANCEL


def test_invalidate_rejects_a_pending_revision_and_naive_times_are_utc() -> None:
    subject = tracker()
    subject.observe(10, 1, START.replace(tzinfo=None), allow_ambient=True)
    pending = subject.observe(10, 2, START.replace(tzinfo=None), allow_ambient=True)
    subject.invalidate(10)

    assert subject.ambient_eligibility(10, pending.revision, START) is None
    snapshot = subject.snapshot(10, START)
    assert snapshot.last_reply_at is None
    assert snapshot.revision > pending.revision
