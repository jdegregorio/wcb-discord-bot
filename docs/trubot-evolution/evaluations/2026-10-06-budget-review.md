# Spending guard candidate review

The before/after reproduction uses the real Discord handlers and API adapter with
an isolated fake provider. Before the change, two synthetic direct events made
two API calls despite a zero-budget environment value: no guard existed. After
maintenance exhaustion, the same two events make zero provider calls and capture
a brief pause message. No actual Discord writes or API charges in these probes.

All 123 regression tests pass with 94.15% branch-inclusive coverage. The suite
covers concurrent reservations, restart persistence, UTC rollover and cross-month
settlement, retained uncertain charges, read-only/corrupt/missing state, unsupported
pricing, retry accounting, cancellation, empty replies, abstention, 13-month
retention, and explicit versus unsolicited depleted-budget behavior.

The bounded candidate live evaluation used the real handler/API path with
synthetic messages, the app-scoped key, and the shared persistent maintenance
ledger. Acceptance: 10/10 transport and agent rubric checks passed. Held-out
variation: 2/2 transport and rubric checks passed. Sox enthusiasm was warm and
relevant in all three core cases; uncertainty, rival preference, fictional identity,
grief, and follow-up abstention remained appropriate. This is a small unblinded
sample, not a measure of long-term character fidelity. Source personality and
model choices are unchanged.

An initial disposable candidate container omitted writable `/tmp`; cleanup failed
after its first accounted call. The staging container was corrected to mirror
production tmpfs. The charge remains in the persistent ledger. The current
production app was unaffected.

Actual token totals are retained in the JSON reports. Estimates use the approved
standard GPT-6 Luna rates, with all noncached input charged conservatively at the
higher cache-write rate. The first covered month's earlier app spending remains
unknown. No paid infrastructure was added. Off-device backup coverage and billing
reconciliation remain follow-up work.
