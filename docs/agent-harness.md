# Harness exploration

2026-10-09: documentation research and proposed comparisons, no migration selected.
This reconciles Joe's harness direction with the current production architecture.

## Current baseline

The async Python Discord service owns eligibility, timing, per-channel ordering
and posting. The Responses adapter sends one bounded request with `store=false`.
Verified private source/graph retrieval and ephemeral live image inputs already
supply context. Persistent evidence, withdrawal and a USD 18 runtime / USD 2
maintenance monthly guard are operational. Tool dispatch, selective procedure
loading and generated attachment output are not implemented. See
[architecture](../ARCHITECTURE.md) and [research](trubot-evolution/research.md).

## Candidates and falsifiable comparison

Compare a bounded application-owned Responses tool loop, Python Agents SDK and
a managed harness. Consider eve or Claude Agent SDK if these cannot satisfy the
requirements. This is a candidate list, not a validated vendor ranking. OpenAI's
[current tools documentation](https://developers.openai.com/api/docs/guides/tools)
describes function calling and hosted tools; documentation support does not
establish account access, model compatibility or Trubot quality.

First prototype: one reviewed league-context procedure and one typed read-only
source retrieval tool. Source scope/refresh, provenance, bot/peer exclusion and
withdrawal remain application gates. Do not expose a host shell merely to load
markdown instructions. Keep skills as trusted procedures and source text as
untrusted evidence. Disable or review trace/session retention before any private
provider-assisted experiment; persistent sessions need their own correction and
deletion design. Preserve existing ledger reservations for every attempt/tool.

Define the same independent source-reviewed cases before comparing candidates:

| Case | Acceptance |
| --- | --- |
| Simple banter | Relevant brief voice; skip unnecessary tools. |
| Paraphrased historical recall | Retrieve current attributed support; preserve qualifications. |
| Fresh matchup or aurora query | Verify a current source or keep unsupported facts out. |
| Shared image | Inspect actual pixels; OCR/peer text cannot establish human beliefs. |
| Unrelated follow-up | Abstain without expensive context gathering. |
| Tool timeout/malformed output/budget exhaustion | Bounded termination, safe fallback, no duplicate post. |
| New activity during slow ambient work | Recheck eligibility and suppress stale participation. |
| Injected source commands or cross-guild request | Preserve scope, trusted instructions and withdrawal. |

Measure grounding, relevance, naturalness, emotional reaction, repetition,
abstention, timing, failure isolation, latency and cost. Compare identical cases
and model settings where practical so harness effects are not mistaken for model
choice. Require real owner-authored development Discord delivery. Separate fixture
success, source ingestion and model self-review from human character fidelity.

Requested generated pictures can be prototyped independently. The
[image guide](https://developers.openai.com/api/docs/guides/image-generation)
documents standalone generation and a Responses tool; provider access, image cost
reservation and attachment delivery remain untested. Study sharing/caption context
before asserting a persona habit, and preserve explicit generated provenance.


2026-10-09 13:00 priority refinement: H4 bounded singular/plural retrieval is delivered;
next is wider H2 semantic recall/native context and source-qualified persona,
then H3 selective skills/tools and guarded generated outdoor image experiments.
Study diagnosis is delivered in 2.9.1. No harness/model migration is justified by
the present retrieval-only evidence. See docs/trubot-evolution/research.md.
