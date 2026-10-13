---
name: "ae-deal-inspection-prep"
description: "Prepare the owning account executive for an internal inspection of one named Summit53 opportunity: a concise, read-only one-page evidence sheet with current deal facts, truthful gaps, likely manager questions, defensible answer evidence, and rep-owned next actions. Use when an AE says 'prepare me for deal inspection', 'prep me for my deal inspection on [deal]', 'help me answer questions on this deal', 'what am I missing before my 1:1', 'give me an inspection cheat sheet', or 'what will my manager ask about [deal]'. Do not use for a manager-led formal deal review deck — use deal-review-prep. Do not use for a contested chronology or 'when did it go dark' — use deal-timeline-defence. Do not use for drafting re-engagement outreach — use deal-action-engine, if installed."
version: "1.1.0"
baselined: "2026-10-13"
status: "active"
---

# AE Deal Inspection Prep

Prepare the owning AE to answer from evidence without pretending that missing qualification,
stakeholder, activity, or next-step data exists. Keep the workflow read-only and concise.

## Route first

Route before reading any data:

| Request | Route |
| --- | --- |
| AE-owned readiness for one named deal: likely questions, evidence gaps, answers, next actions | Use this skill |
| Manager-led formal deal review, pipeline-review deck, broad coaching assessment, or executive artifact | Route to `deal-review-prep` |
| Challenged chronology, disputed activity sequence, "when did it go dark", or rescue-decision defence | Route to `deal-timeline-defence` |
| Draft or send re-engagement outreach, write a CRM note, or execute an action | Route to `deal-action-engine`, if installed; do not perform it here |

Persona language alone is insufficient. A manager asking for an AE's formal review deck still
belongs to `deal-review-prep`; an AE challenging the chronology still belongs to
`deal-timeline-defence`.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its
checklist before any data call. It covers connector and tenant resolution
(`current_context` first, `scoped_org_id`), loading deferred tools in one ToolSearch batch,
`list_available_tools` and live-schema inspection, read-only discipline, fixture exclusion,
unavailable-not-zero, correlational language, and delivery.

Skill-specific gates, stricter than the preflight:

1. Stop before any opportunity lookup if tenant scope is missing or mismatched.
2. Resolve exactly one opportunity by ID or an unambiguous search. Confirm the requester is
   the owning AE when ownership materially affects access or the framing of actions.
3. Require a non-empty `get_opportunity` payload whose `id` and opportunity citation match
   the selected ID.
4. Compare `current_context.user.id` with the opportunity `owner_id`. When they differ,
   require explicit on-behalf-of framing, or route a manager-led request to
   `deal-review-prep`.
5. Read-only: never create notes, update CRM fields, draft or send messages, create
   interventions, or invoke approval-gated actions.
6. Demo label (commercial use): when the connector or `current_context` identifies a demo,
   test, or staging deployment and provenance is not reliable on every row, label every
   output exactly **Demo data — not for customer or commercial decisions.**

## Gather the minimum evidence

Use logical capabilities only when exposed and permitted. Inspect each live schema first.

| Capability | Purpose |
| --- | --- |
| `current_context` | Confirm current organization and viewer context |
| `search_opportunities` | Resolve a supplied deal or account name when no ID is given |
| `get_opportunity` | Current deal, owner, stage, amount, close date, category, and freshness |
| `get_opportunity_notes_summary` | Bounded deal narrative; fall back to recent `get_opportunity_notes` |
| `get_opportunity_activities` | Recent cadence, last observed touch, and recorded next-step evidence |
| `list_methodology_playbooks` | Resolve the published framework definition; ask the user if more than one active framework remains |
| `opportunity_framework_summary` | Qualification evidence for the selected supported framework; do not average absent elements |
| `get_opportunity_signals` | Access-gated ranked constraint and movement; optional, never a blocker |
| `opportunity_stakeholder_intelligence` | Buying-committee coverage and explicit gaps; optional |
| `search_target_accounts`, `get_target_account` | Optional, Outreach plan: committee coverage from the converted outreach target account (see below) |
| `risk_heatmap` | Optional portfolio response: page and select the exact opportunity ID locally, disclose coverage, and treat bounded-page absence as unavailable |
| `meeting_capture_history` | Optional, access-gated: recorded calls for this deal (filter by `opportunity_id`; default `view` is the caller's own sessions) |
| `meeting_context` | Optional, access-gated: bounded intelligence for one recorded session by `session_id`; request a transcript only when a specific question needs it, and keep it within the capped segment and character limits |

Retrieve bounded results sufficient for the inspection horizon. Disclose truncation. Do not
pull a broad account or team review merely to fill the page.

**Recorded call evidence (optional).** When `meeting_capture_history` is exposed and permitted,
list sessions for the exact `opportunity_id` within the inspection horizon, then read at most
the two or three most relevant sessions with `meeting_context`. Use them to corroborate or
contradict what the notes say a buyer committed to. Cite each as session ID plus start time.
Treat meeting intelligence as observed only for what the session record states; model-produced
summaries inside it are still **Inferred**. If the capability is unavailable, denied, or returns
no session for the deal, record "recorded call evidence unavailable" in Sources and limits —
never "no calls happened".

**Target-account committee coverage (optional, Outreach plan).** When the opportunity came
from a converted outreach target account and the tools are exposed and permitted, call
`search_target_accounts` with `query` set to the account name and use a result only when its
`opportunity_id` equals the selected opportunity (or its `crm_account` matches and the AE
confirms). Then read `get_target_account(target_account_id)`: `coverage.roles[]` (missing,
mapped, engaged), `coverage.gaps`, and each committee member's `engaged` and
`last_touch_date`. Record mapped and engaged roles and the required-role gaps (for example "no
economic buyer engaged") as **Observed — target-account record** with dates, under What the
evidence says and Gaps to acknowledge; they also make good likely questions ("Who has spoken to
the economic buyer since conversion?"). A single-threaded account has `coverage_pct: null` by
design: coverage not measured, never 0%. If the tools are unavailable, plan-gated, denied or no
target account matches, note "target-account coverage unavailable" in Sources and limits and
continue. Never write to target accounts or stakeholder suggestions.

**MEDDPICC partial rule.** The live methodology asset may identify `MEDDPICC` while the
summary capability accepts `MEDDPIC`. Use only a token explicitly supported by the live
capability, label that analysis **Partial — Competition component unavailable**, and never
present the seven-component result as full MEDDPICC completion.

**Owner reconciliation.** Reconcile any signal-recommended actor with the authoritative
opportunity owner; suppress a named assignment when they differ.

## Prepare the inspection pack

1. **Snapshot:** State current deal facts and source freshness. Keep tool-provided scores
   separate from model judgment; follow the response's score semantics.
2. **Rep narrative:** Summarize what has happened in three to five evidence-grounded lines.
   Label notes as authored narrative, activities as observed events, and recorded calls as
   session evidence.
3. **Truthful gaps:** List missing or weak qualification, stakeholder, activity, commitment,
   timing, and next-step evidence. Missing evidence is a gap, not a negative fact.
4. **Likely inspection questions:** Write five to eight specific questions a manager could
   reasonably ask. Ground each in a cited fact or gap.
5. **Defensible answer prompts:** For each question, provide the evidence the AE can cite and
   an explicit "say this is unknown" line where proof is missing. Do not fabricate an answer.
6. **Rep-owned next actions:** Suggest three to five prioritized actions with owner, intended
   timing, success evidence, and dependency. These are recommendations only; execute none.
7. **Confidence limits:** State stale, missing, denied, conflicting, or fixture-filtered inputs.

Do not create a performance judgment about the AE. Do not convert the pack into manager
coaching, promotion/PIP evidence, or a broad deal-health deck.

## Evidence rules

- Cite the source and as-of time for every material claim.
- Mark facts as **Observed**, model synthesis as **Inferred**, conflicts as **Disputed**, and
  inaccessible or absent evidence as **Unavailable**.
- Never convert `null`, empty arrays, access denial, or unavailable tools to zero or health.
- Do not infer customer intent, stakeholder authority, owner, timestamp, or commitment.
- Do not infer close-date history from the current close date or update timestamp.
- Treat signal movement and activity correlations as non-causal.
- Exclude `synthetic`, `demo_seed`, `demo_fixture`, seeded, generated-test, and other
  fixture-marked rows from real counts (see the preflight for the full marker list).

## Deliver

Default to a one-page in-chat or Markdown inspection sheet with these sections:

- Deal snapshot
- What the evidence says
- Gaps to acknowledge
- Likely questions and answer evidence
- Rep-owned next actions
- Sources and limits

Do not create a PPTX unless the user explicitly requests a personal one-page aid and the
request remains AE-owned. If they do, build it with the `pptx` skill and render and inspect
the slide before delivery. Route any formal pipeline-review or manager-facing deck to
`deal-review-prep`.

## Verify before delivery

- [ ] The organization, opportunity, and owner are unambiguous; returned IDs match
      `scoped_org_id` and the selected opportunity.
- [ ] Every claimed fact is cited and freshness is visible.
- [ ] Each proposed answer distinguishes known evidence from unknowns.
- [ ] Any MEDDPICC analysis run on a seven-component token is labelled
      **Partial — Competition component unavailable**.
- [ ] Recorded-call evidence, if used, is cited by session and its absence is never read as
      "no calls".
- [ ] Target-account coverage, if used, matched by `opportunity_id` (or AE-confirmed), is
      labelled Observed with dates, and no target-account write was called.
- [ ] No timeline dispute was handled here instead of `deal-timeline-defence`.
- [ ] No manager-led formal review was handled here instead of `deal-review-prep`.
- [ ] Fixture evidence is excluded from real counts and the exact demo label is present when
      required.
- [ ] No CRM write, email action, intervention mutation, or approval-gated action was called.
