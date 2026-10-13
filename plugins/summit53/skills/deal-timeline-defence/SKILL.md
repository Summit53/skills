---
name: "deal-timeline-defence"
description: "Reconstruct a defensible, read-only chronology for one Summit53 opportunity when a close date, activity sequence, ownership or stakeholder handoff, intervention, or dark-deal rescue decision is challenged. Returns a one-line verdict plus a timestamped chronology that separates observed, corroborated, inferred, disputed, and unavailable evidence. Use for requests such as 'what actually happened on this deal', 'defend this timeline', 'when did the deal go dark', 'show the evidence trail', 'who owned this deal when it slipped', or 'should we start a dark-deal rescue'. Do not use for a manager-led formal deal review deck — use deal-review-prep. Do not use for an AE's own inspection prep — use ae-deal-inspection-prep. Do not use for drafting re-engagement outreach or a CRM note — use deal-action-engine, if installed."
metadata:
  version: "1.0.0"
  baselined: "2026-10-13"
  status: "active"
---

# Deal Timeline Defence

Produce a concise chronology that separates timestamped facts, bounded interpretations, and
missing evidence. Keep the workflow read-only.

## Route first

Route before reading data:

| Request | Route |
| --- | --- |
| Challenged chronology, inactivity onset, close-timing claim, handoff, or rescue-decision evidence | Use this skill |
| Manager-led formal review, pipeline-review deck, broad deal health, or coaching questions | Route to `deal-review-prep` |
| AE asks to prepare their own answers, evidence gaps, and next actions for an inspection | Route to `ae-deal-inspection-prep` |
| Draft or send re-engagement email, create a CRM note, or execute a rescue | Route to `deal-action-engine`, if installed; do not perform it here |

If the request mixes timeline defence with another route, complete the chronology only and
state which remaining part belongs elsewhere.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its
checklist before any data call. It covers connector and tenant resolution
(`current_context` first), deferred-tool loading, `list_available_tools` and live-schema
inspection (capability names below are semantic dependencies, not fixed schemas), read-only
discipline, fixture exclusion, unavailable-not-zero, correlational language, and delivery.

Skill-specific gates, stricter than the preflight:

1. Stop before opportunity lookup if tenant scope is missing or mismatched.
2. Resolve exactly one opportunity by ID or an unambiguous search result. Ask the user to
   select when multiple matches remain.
3. Require a non-empty `get_opportunity` payload whose `id` and opportunity citation match
   the selected ID **before any other deal-specific read**. Empty or mismatched evidence is a
   stop.
4. Read-only: **never call `create_opportunity_note`**, send or draft email, create or update
   an intervention, or invoke any approval-gated execution tool.
5. Demo label (commercial use): when the connector or `current_context` identifies a demo,
   test, or staging deployment and provenance is not reliable on every row, label every
   output exactly **Demo data — not for customer or commercial decisions.**

## Gather the minimum evidence

Use these logical capabilities when exposed and permitted:

| Capability | Purpose | Handling |
| --- | --- | --- |
| `current_context` | Confirm current organization and viewer context | Stop on an organization mismatch |
| `search_opportunities` | Resolve a supplied deal or account name | Use only when no opportunity ID is supplied; resolve ambiguity |
| `get_opportunity` | Authoritative current stage, owner, amount, close date, and update time | Required baseline; missing fields stay unavailable |
| `get_opportunity_activities` | Timestamped opportunity activity sequence | Retrieve enough bounded history for the disputed interval; disclose truncation |
| `activity_gaps` | Account-level inactivity corroboration | Set the tested `days`, filter by owner server-side (`owner_ids`), then match the returned row to the exact account ID locally; absence is unavailable, not proof of no gap |
| `list_interventions` | Deal/account intervention ledger | Filter by `entity_type` and `entity_id`; describe as execution records, not coaching |
| `prepare_dark_deal_rescue` | Optional shadow-mode rescue diagnosis | Inspect runtime metadata; call only while the read is classified read-only and `requires_approval=false`; use diagnosis and evidence only, never its drafts |
| `opportunity_stakeholder_intelligence` | Optional, access-gated: stakeholder profiles, engagement moves, and coverage gaps for ownership/stakeholder handoff questions | Use only timestamps the payload states; never infer a handoff date or actor from it |
| `meeting_capture_history` | Optional, access-gated: recorded call sessions for the deal | Filter by `opportunity_id` and the disputed date window (`date_start`/`date_end`); page through results and disclose truncation; team view is leader-only |
| `meeting_context` | Optional, access-gated: bounded intelligence for one recorded session by `session_id` | Request a transcript only when a disputed event needs it, within the capped segment and character limits; never returns audio |

Use `get_opportunity_notes_summary` or bounded `get_opportunity_notes` only when a disputed
event needs qualitative context. Label notes as authored narrative, not independent proof.

**Recorded calls (optional).** A captured session with a start timestamp is an independent
**Observed** event and can corroborate an activity row or contradict a "went dark" claim
within the interval. Summaries or extracted commitments inside `meeting_context` are model
output: label them **Inferred** unless the transcript segment itself is quoted. If the
capability is unavailable, denied, or returns no session, record "recorded-call evidence
unavailable" in Sources and limits — never "no meetings occurred". Meeting capture coverage is
not complete activity coverage.

**Ownership and stakeholder handoffs (optional).** Use the current `get_opportunity` owner as
the only authoritative owner. Use `opportunity_stakeholder_intelligence` to evidence buyer-side
stakeholder changes (champion departure, new economic buyer, coverage gaps) and only those
engagement moves that carry their own timestamps. It is not an owner-history log: if no source
exposes a prior owner and a change timestamp, report the seller-side handoff as
**Unavailable**. Treat its risk summary as model-derived, kept separate from observed events.

**Shadow-mode rescue.** `prepare_dark_deal_rescue` currently returns a read-only shadow packet
and separately marks execution of nested proposals as approval-gated. Re-check the live
contract before every call. Call it **only while** the read is classified read-only and
`requires_approval=false`. If the read itself is unavailable, write-capable, or
`requires_approval=true`, do not call it without an explicit user request and approval. Use
its diagnosis and evidence only; **never reuse or reproduce its drafts**, and never present
them as executed actions.

## Build the chronology

1. Define the challenged interval and the claim being tested. If neither is clear, state the
   narrow interpretation used.
2. Normalize displayed timestamps to the user's timezone while preserving each source
   timestamp in the evidence citation. Do not invent a time for date-only fields.
3. Order events by observed timestamp. For equal or missing timestamps, retain source order
   and flag sequencing uncertainty.
4. Separate event types: CRM state, activity, recorded call, note, stakeholder change,
   intervention, and model-derived signal.
5. Identify the last observed activity, any silence interval, close-date status, owner or
   stakeholder handoffs supported by evidence, and relevant interventions.
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
seeded, generated-test, or otherwise fixture-marked rows from real event counts.

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
   fixture exclusions, optional capabilities used or unavailable, and non-causal caveats.

Default to an in-chat brief or Markdown artifact. Do not create a presentation unless the user
explicitly asks for one (then use the host presentation toolchain in
[host-adapters.md](references/host-adapters.md#building-slides), and render and inspect every
slide); a formal manager review deck remains `deal-review-prep`.

## Verify before delivery

- [ ] The opportunity and organization are unambiguous; returned IDs match `scoped_org_id`
      and the selected opportunity.
- [ ] Every timeline event has a source and timestamp or is marked unavailable.
- [ ] No current field is presented as historical movement.
- [ ] Account-level gaps are not presented as deal-level activity proof.
- [ ] If the bounded activity page does not cover the disputed interval, chronology coverage
      is explicitly incomplete; a missing account row from `activity_gaps` is never "no gap".
- [ ] Recorded-call and stakeholder evidence, if used, is cited by record and timestamp; its
      absence is never read as "no meeting" or "no handoff".
- [ ] Intervention timing is not presented as causal evidence or coaching delivered.
- [ ] Rescue content is labelled shadow-mode, was read only while `requires_approval=false`,
      and no proposed draft is reproduced or presented as an action.
- [ ] Synthetic or fixture evidence is excluded from real counts and labelled when present.
- [ ] No `create_opportunity_note`, write, email, intervention mutation, or approval-gated
      execution was called.
