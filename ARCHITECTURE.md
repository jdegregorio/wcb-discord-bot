# Architecture

Trubot is intentionally a small service. The design separates policy from I/O
so Discord events, OpenAI requests, timing rules, and the personality can change
independently without hiding behavior behind a framework.

## Runtime flow

```text
Discord event
    │
    ▼
TruBotClient ── validates channel + trigger ──┐
    │                                         │
    │                                  ParticipationTracker
    │                                  (pure per-channel policy)
    ▼                                         │
recent Discord history ◄──────────────────────┘
    │
    ▼
OpenAITruaxResponder
    ├── personality + mode contract
    ├── Responses API / gpt-5.6-luna
    ├── reasoning.effort = none
    └── store = false
    │
    ▼
bounded Discord reply
```

## Boundaries

- `config.py` parses and validates the entire environment at startup. Secrets
  cannot appear in the settings representation.
- `personality.py` is the only source of character instructions and authentic
  examples. Prompt plumbing never owns character decisions.
- `openai_responder.py` is the only OpenAI dependency. It produces a plain
  string through the Responses API and normalizes accidental speaker prefixes.
- `participation.py` is a synchronous state machine. Given channel activity and
  time, it decides whether an ambient reply may be scheduled. It performs no
  sleeping, network access, or Discord calls.
- `history.py` converts Discord objects into provider-neutral conversation
  messages, ignores other bots, and bounds untrusted content.
- `discord_client.py` is the orchestration shell. It owns pending tasks,
  per-channel response locks, reactions, replies, and graceful shutdown.
- `health.py` ties container readiness to the live Discord session rather than
  merely proving that a Python process exists.
- `app.py` is the composition root. Importing any module is side-effect free.

## Participation invariants

For each channel, the tracker retains a rolling set of human activity, the last
successful Trubot reply, a UTC daily ambient count, and a monotonically
increasing revision.

1. Every new human message invalidates the previous quiet-period revision.
2. An ambient task can post only if its revision is still current after the
   delay.
3. At least the configured number of distinct humans must remain inside the
   activity window.
4. A successful direct, reaction, or ambient reply starts the ambient cooldown.
5. Only ambient replies consume the daily quota.
6. Restarting clears ephemeral state; it never manufactures historical state
   from Discord messages.

The event loop serializes tracker mutations. A per-channel `asyncio.Lock`
prevents direct, reaction, and ambient generations from posting concurrently.

## Failure behavior

- OpenAI timeouts and transient errors use the SDK retry budget.
- Direct and reaction failures receive one short in-character fallback; ambient
  failures are logged and stay silent to avoid unsolicited error spam.
- Failed generations do not consume the ambient quota.
- Discord send/fetch failures are logged with IDs, never message contents or
  credentials.
- Disconnecting removes readiness immediately. Resuming recreates and refreshes
  it; shutdown cancels pending ambient work and closes the OpenAI client.

## Privacy and safety

Only the configured rolling Discord history is sent to OpenAI. Responses are
requested with storage disabled. The API receives a stable SHA-256 identifier
scoped to the Discord guild and requesting user, not their display name or raw
Discord ID. Generated messages cannot create Discord mentions.
