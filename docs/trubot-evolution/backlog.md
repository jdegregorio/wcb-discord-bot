# Prioritized backlog

Replenish this list as evidence arrives. Each run owns prioritization and carries
one coherent increment through production verification.

## 1. Evidence-backed preference retrieval

- Acceptance: derive a compact set of interests and style observations with source
  references, confidence, timestamps, and contradiction/expiry handling. Retrieve
  only relevant evidence within a token budget. Andrew's preferences must come
  from his attributed messages, never another person's enthusiasm or bot output.
- Dependencies: verified ingestion and spending guard, delivered in 2.3.0/2.2.0.
  Revalidate source freshness before deriving beliefs, including sources not yet
  revisited by rotating reconciliation after an offline interval.
- Validation: supported enthusiasm, rival preferences, stale sports beliefs,
  corrections, unsupported claims, and prompt injection. Compare against the
  emotional-judgment fixtures and add private held-out evidence evaluations.

## 2. Participation and emotional continuity

- Acceptance: respond naturally to clear contextual invitations and remember
  relevant emotional context, while abstaining from side conversations and grief
  jokes. Measure useful participation without increasing unsolicited frequency.
- Dependencies: retrieval and more observed evaluation evidence.
- Validation: direct/reaction/follow-up/ambient scenarios, competing recipients,
  changing topics, bot mistakes, and held-out warm or difficult conversations.

## 3. Cost reconciliation and off-device recovery

- Acceptance: reconcile provider billing with conservative token estimates; verify
  encrypted off-device backup and restoration without resetting current balances.
- Dependencies: billing read access and the platform backup path. The app key
  does not grant administrative billing visibility. First covered month has
  unknown spending before the guard. No claim of a provider-enforced account cap.
- Evidence: the SDK exposes cached tokens but no separate cache-write counts.
  Current estimates use the higher cache-write rate for all noncached input.
- Validation: pricing drift review, uncertain-request corrections based on billing,
  recovery after a newer request, and no access expansion or credential leakage.

## Completed

- 2026-10-07 complementary run: durable operator withdrawal, local evidence and
  backup cleanup, protection against stale database restoration, loaded-worker
  shutdown, and preservation of spending state. Version 2.3.1 candidate; release
  and production verification are tracked in progress.md.

- 2026-10-07: verified private identity and incremental intake, atomic per-channel
  checkpoints, live events, bounded historical catch-up, edit/delete race guards,
  offline reconciliation, configurable retention and recovery. Version 2.3.0.
  Intake makes no model calls; evidence does not affect replies yet.

- 2026-10-06: persistent API token accounting, conservative reservations before
  every attempt, accounted retries, UTC monthly allowance with maintenance reserve,
  fail-closed storage/pricing, and bounded evaluation on the same private ledger.
  Version 2.2.0. Release and deployment evidence is recorded in progress.md.


- 2026-10-05: emotional judgment, topical enthusiasm, current-fact uncertainty,
  fictional identity boundaries, and grounded baseball allegiance. Version 2.1.2
  uses bounded contextual reasoning for inferred follow-ups. Release/production evidence is tracked in
  [progress.md](progress.md). Added bounded synthetic event-handler evaluation;
  it captures outputs without posting into Discord.

## 4. Learning continuity and freshness

- Acceptance: observe catch-up lag privately, establish backup coverage, and
  shorten reconciliation time where measured volume justifies it. Keep deleted
  or unverified sources unavailable to future belief extraction.
- Dependencies: real bounded-intake volume and retrieval design. Current limit is
  two source rechecks per channel per five-minute cycle, so offline repairs are
  eventual; no claim of full-history freshness or complete initial backfill.
- Validation: large-channel interruption/recovery, extended outages, permission
  loss, shrinking allowlists, retention and correction reflected in derived data.
- Withdrawal markers must accompany disaster recovery. Validate encrypted
  off-device deletion and recovery; current command covers documented local copies.
