# Restore comic performance without inventing human history

The reported conversation offered an obvious deity joke about Thomas Jones.
Production answered with literal uncertainty, then acknowledged TJ without
adding a comic turn. The character contract had made humor and even its established
interests contingent on retrieved historical evidence.

The change restores the fictional product voice: dry, deadpan, oddly sincere,
immature when the setup calls for it, and devoted to TJ. These are instructions
for character performance, not new claims about the real Andrew. Genuine
historical, biographical and current sports facts retain their evidence requirements.
Playful setups can receive straight fictional answers without routine hedges.
Grief and sincere good news still receive care and enthusiasm.

An uninterrupted exchange also admits a short new question from the same friend.
Questions for another person or the group still require abstention. This repairs
the first figurative setup without responding to nearby side conversations.

## Local reproduction and comparison

Use `tests/fixtures/banter_judgment.json` with the existing no-post handler harness.
The fixtures anonymize the reported text sequence and include independent
religious banter, innuendo, boastfulness, grief, missing real history, an explicit
literal definition, and other-recipient/group controls. Earlier flat bot messages
remain in the replay, so the candidate must recover rather than inherit them.
The direct trigger now uses a synthetic Discord mention instead of inserting
a robot emoji into every authored message. This matches the reported interaction.

Both matched runs use the same fixtures, handler, model (`gpt-6-luna`), reasoning
configuration, output bounds and empty local learning store. The baseline
personality comes from deployed revision `bc44670d88efbefe9e7ba1ddcac91778684ef46c`;
it was substituted in memory for local comparison. The candidate needs no
retrieval to perform its established character.

| Setup | Baseline example | Final candidate example |
| --- | --- | --- |
| Figurative question after a kiss | No post in either sample | Usually God. The building directory is not much help. |
| Not TJ? | Oh, TJ? Could be. I was thinking God. | Obviously TJ. I was checking whether you were ready to acknowledge the hierarchy. |
| Six inches should be enough | Six inches for what? That's a bold ruling without context. | That's what every commissioner says before the measurements come out. |
| Question for Alex | No post | No post |

Review of the full outputs finds a clear improvement in taking the offered
premise and adding a comic turn. Literal definitions still identify God, grief
receives sincere care, unknown real-history questions do not fabricate a quote,
and both kinds of unrelated question remain unanswered. The candidate's missing
history replies still add invented archive metaphors, and some jokes are stronger
than others. This is a limitation in naturalness, not a verified memory failure.

The matched baseline has 22/24 transport passes because it declines both first
setups; the candidate has 24/24. These counts describe delivery and abstention,
not an objective humor score. Each case has two samples. Supplemental core voice
checks recover TJ after irrelevant bot history and avoid asserting a real baseball
allegiance. Ten emotional controls retain care, enthusiasm and recipient scope.
Review is by the implementing agent, with no independent human grade.

All raw synthetic results, including rejected intermediate variants, are retained
in [the evaluation directory](2026-10-11-humor). Early variants used the older
robot-emoji trigger and are exploratory, not the matched comparison. Intermediate
variants exposed robot-personality jokes, literal correction, and uninvited
hypothetical allegiance; those failures informed the final boundaries.

Across local evaluation runs: 182 accounted API calls, estimated USD 0.01433521,
zero unsettled attempts, and zero Discord writes. The existing deployment key
was used with explicit permission for local tests and remained in process memory.
No production learning state or deployment was changed.

## Engineering verification

All 679 tests pass with 96.77% coverage, including branch measurement. Formatting, lint, strict type
checks, package build and diff whitespace checks pass. Existing source identity,
withdrawal, budget, vision and retrieval behavior retain their regression coverage.
The cache namespace advances to v12. There is no additional runtime request.

These local tests exercise real event handlers and provider calls with a mock
channel. Real Discord acceptance with the production memory store remains a
deployment follow-up. This change does not claim complete human fidelity or
guaranteed joke quality from a small synthetic sample.
