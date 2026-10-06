# Prioritized backlog

Replenish this list as evidence arrives. Each run owns prioritization and carries
one coherent increment through production verification.

## 1. Verified identity and incremental private message ingestion

- Acceptance: pin the confirmed stable Discord ID privately with authenticated
  membership evidence; ingest only its messages from the existing channel allowlist,
  preserving attribution and source timestamps with per-channel checkpoints.
- Dependencies: persistent storage and spending guard. An initial metadata audit
  found corroborated author/member information; repeat it when pinning the ID.
  No ID or message content is recorded in this public repository.
- Bound catch-up batches and schedule them so live replies continue. Exclude bot
  outputs and distinguish context from Andrew's evidence. Support edits/deletions,
  configurable retention, correction, deletion, backup, and recovery.
- Validation: ambiguous candidates stop learning, duplicate ingestion is idempotent,
  interrupted catch-up resumes, other users cannot contaminate attribution, and
  reconnects do not lose checkpoints or replay unbounded history.

## 2. Evidence-backed preference retrieval

- Acceptance: derive a compact set of interests and style observations with source
  references, confidence, timestamps, and contradiction/expiry handling. Retrieve
  only relevant evidence within a token budget. Andrew's preferences must come
  from his attributed messages, never another person's enthusiasm or bot output.
- Dependencies: verified ingestion and spending guard.
- Validation: supported enthusiasm, rival preferences, stale sports beliefs,
  corrections, unsupported claims, and prompt injection. Compare against the
  emotional-judgment fixtures and add private held-out evidence evaluations.

## 3. Participation and emotional continuity

- Acceptance: respond naturally to clear contextual invitations and remember
  relevant emotional context, while abstaining from side conversations and grief
  jokes. Measure useful participation without increasing unsolicited frequency.
- Dependencies: retrieval and more observed evaluation evidence.
- Validation: direct/reaction/follow-up/ambient scenarios, competing recipients,
  changing topics, bot mistakes, and held-out warm or difficult conversations.

## 4. Cost reconciliation and off-device recovery

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

- 2026-10-06: persistent API token accounting, conservative reservations before
  every attempt, accounted retries, UTC monthly allowance with maintenance reserve,
  fail-closed storage/pricing, and bounded evaluation on the same private ledger.
  Version 2.2.0. Release and deployment evidence is recorded in progress.md.


- 2026-10-05: emotional judgment, topical enthusiasm, current-fact uncertainty,
  fictional identity boundaries, and grounded baseball allegiance. Version 2.1.2
  uses bounded contextual reasoning for inferred follow-ups. Release/production evidence is tracked in
  [progress.md](progress.md). Added bounded synthetic event-handler evaluation;
  it captures outputs without posting into Discord.
