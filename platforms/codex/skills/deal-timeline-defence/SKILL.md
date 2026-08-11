---
name: deal-timeline-defence
description: Reconstruct a defensible, read-only chronology for one Summit53 opportunity when a close date, activity sequence, ownership handoff, intervention, or dark-deal rescue decision is challenged. Use for requests such as "what actually happened on this deal", "defend this timeline", "when did the deal go dark", "show the evidence trail", or "should we start a dark-deal rescue". Do not use for a manager-led formal deal-review deck, an AE's general inspection prep, or drafting re-engagement outreach.
---

# Deal Timeline Defence

Produce a concise chronology that separates timestamped facts, bounded interpretations,
and missing evidence. Keep the workflow read-only.

## Route before reading data

| Request | Route |
| --- | --- |
| Challenged chronology, inactivity onset, close-timing claim, handoff, or rescue-decision evidence | Use this skill |
| Manager-led formal review, pipeline-review deck, broad deal health, or coaching questions | Route to `$deal-review-prep` |
| AE asks to prepare their own answers, evidence gaps, and next actions for an inspection | Route to `$ae-deal-inspection-prep` |
| Draft or send re-engagement email, create a CRM note, or execute a rescue | Route to `$deal-action-engine` when available; do not perform it here |

If the request mixes timeline defence with another route, complete the chronology only and
state which remaining part belongs elsewhere.

## Resolve scope and tools

1. Use the connected **Summit53** connector by the logical capability names in this file. Resolve the
   exposed tool dynamically; never hard-code an MCP prefix, generated hash, or namespace.
2. Discover `list_available_tools`, then discover the exact schema for each capability
   before calling it. Capability names below are semantic dependencies, not fixed schemas.
3. Call `current_context`. Require a non-empty `organization.id`, an active organization and
   user, and approved membership. Stop before opportunity lookup if tenant scope is missing
   or mismatched.
4. Resolve exactly one opportunity by ID or an unambiguous search result. Ask the user to
   select when multiple matches remain.
5. Require a non-empty `get_opportunity` payload whose `id` and opportunity citation match
   the selected ID before any other deal-specific read. Empty or mismatched evidence is a stop.
6. Use only read-only calls. Never call `create_opportunity_note`, send or draft email,
   create or update an intervention, or invoke any approval-gated execution tool.

## Gather the minimum evidence

Use these logical capabilities when exposed and permitted:

| Capability | Purpose | Handling |
| --- | --- | --- |
| `current_context` | Confirm current organization and viewer context | Use when exposed; stop on an organization mismatch |
| `search_opportunities` | Resolve a supplied deal or account name | Use only when no opportunity ID is supplied; resolve ambiguity |
| `get_opportunity` | Authoritative current stage, owner, amount, close date, and update time | Required baseline; missing fields stay unavailable |
| `get_opportunity_activities` | Timestamped opportunity activity sequence | Retrieve enough bounded history for the disputed interval; disclose truncation |
| `activity_gaps` | Account-level inactivity corroboration | Set the tested `days`, filter by owner server-side, then match the returned row to the exact account ID locally; absence is unavailable, not proof of no gap |
| `list_interventions` | Deal/account intervention ledger | Filter by `entity_type` and `entity_id`; describe as execution records, not coaching |
| `prepare_dark_deal_rescue` | Optional shadow-mode rescue diagnosis | Inspect runtime metadata; call only while the read is classified read-only and `requires_approval=false`; use diagnosis and evidence only, never its drafts |

Use `get_opportunity_notes_summary` or bounded `get_opportunity_notes` only when a disputed
event needs qualitative context. Label notes as authored narrative, not independent proof.

`prepare_dark_deal_rescue` currently returns a read-only shadow packet and separately marks
execution of nested proposals as approval-gated. Re-check the live contract before every call.
If the read itself is unavailable, write-capable, or `requires_approval=true`, do not call it
without an explicit user request and approval. Never reproduce its drafts as executed actions.

## Build the chronology

1. Define the challenged interval and the claim being tested. If neither is clear, state the
   narrow interpretation used.
2. Normalize displayed timestamps to the user's timezone while preserving each source
   timestamp in the evidence citation. Do not invent a time for date-only fields.
3. Order events by observed timestamp. For equal or missing timestamps, retain source order
   and flag sequencing uncertainty.
4. Separate event types: CRM state, activity, note, intervention, and model-derived signal.
5. Identify the last observed activity, any silence interval, close-date status, owner
   handoffs supported by evidence, and relevant interventions.
6. Do not infer historical close-date movement from the current close date, same-stage rows,
   update timestamps, or text that mentions slippage. Report it as unavailable unless the
   source exposes both prior and current close dates.
7. Treat Intervention Ledger outcomes as correlational. Missing completion is not failure,
   and an intervention timestamp does not prove that it caused later movement.
8. Compare independent evidence before reaching a decision. A notes summary may explain a
   gap but cannot replace an absent activity timestamp.

## Evidence status rules

Use only these statuses:

- **Observed** — directly present in a cited source.
- **Corroborated** — present in at least two independent sources.
- **Inferred** — a bounded interpretation from stated observations.
- **Disputed** — sources conflict and the conflict cannot be resolved.
- **Unavailable** — the required source or field is missing, denied, or truncated.

Never convert `null`, an empty result, an access denial, or an unavailable capability to zero,
"no risk", or "did not happen". Never infer an owner, actor, timestamp, or customer intent.

Inspect provenance and free-text markers. Exclude `synthetic`, `demo_seed`, `demo_fixture`,
seeded, generated-test, or otherwise fixture-marked rows from real event counts. When the
connector or `current_context` identifies a demo, test, or staging deployment and provenance
is not reliable on every row, label every output exactly:
**Demo data — not for customer or commercial decisions.**

## Deliver the defence brief

Return a compact response with:

1. **Scope and tested claim** — opportunity, interval, timezone, and decision in question.
2. **Verdict** — supported, partly supported, unsupported, or indeterminate; one sentence.
3. **Chronology** — timestamp, event, source, evidence status, and relevance.
4. **What is proven / inferred / missing** — keep the three categories separate.
5. **Dark-deal rescue decision** — warranted, not warranted, or indeterminate, with the
   observed rule and evidence. Do not include rescue-email or CRM-note drafts.
6. **Next evidence to obtain** — only material gaps that could change the verdict.
7. **Sources and limits** — logical capabilities, as-of times, access limits, truncation,
   fixture exclusions, and non-causal caveats.

Default to an in-chat brief or Markdown artifact. Do not create a presentation unless the user
explicitly asks for one; a formal manager review deck remains `$deal-review-prep`.

## Verify before delivery

- The opportunity and organization are unambiguous.
- Every timeline event has a source and timestamp or is marked unavailable.
- No current field is presented as historical movement.
- Account-level gaps are not presented as deal-level activity proof.
- If the bounded activity page does not cover the disputed interval, chronology coverage is
  explicitly incomplete; a missing account row from `activity_gaps` is never "no gap".
- Intervention timing is not presented as causal evidence or coaching delivered.
- Rescue content is labelled shadow-mode and no proposed draft is reproduced as an action.
- Synthetic or fixture evidence is excluded from real counts and labelled when present.
- No write, email, note, intervention mutation, or approval-gated execution was called.
