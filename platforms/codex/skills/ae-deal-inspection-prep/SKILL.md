---
name: ae-deal-inspection-prep
description: Prepare an account executive for an internal inspection of one named Summit53 opportunity with a concise, read-only evidence pack covering current facts, truthful gaps, likely questions, defensible answers, and rep-owned next actions. Use when an AE says "prepare me for deal inspection", "help me answer questions on this deal", "what am I missing before my 1:1", or "give me an inspection cheat sheet". Do not use for manager-led formal deal-review decks, challenged timeline reconstructions, or outreach drafting.
---

# AE Deal Inspection Prep

Prepare the owning AE to answer from evidence without pretending that missing qualification,
stakeholder, activity, or next-step data exists. Keep the workflow read-only and concise.

## Route before reading data

| Request | Route |
| --- | --- |
| AE-owned readiness for one named deal: likely questions, evidence gaps, answers, next actions | Use this skill |
| Manager-led formal deal review, pipeline-review deck, broad coaching assessment, or executive artifact | Route to `$deal-review-prep` |
| Challenged chronology, disputed activity sequence, "when did it go dark", or rescue-decision defence | Route to `$deal-timeline-defence` |
| Draft or send re-engagement outreach, write a CRM note, or execute an action | Route to `$deal-action-engine` when available; do not perform it here |

Persona language alone is insufficient. A manager asking for an AE's formal review deck still
belongs to `$deal-review-prep`; an AE challenging the chronology still belongs to
`$deal-timeline-defence`.

## Resolve scope and tools

1. Use the connected **Summit53** connector by the logical capability names in this file. Resolve the
   exposed tool dynamically; never hard-code an MCP prefix, generated hash, or namespace.
2. Discover `list_available_tools`, then discover the exact schema for every capability
   before calling it. Do not infer parameters from another deployment.
3. Call `current_context`. Require a non-empty `organization.id`, an active organization and
   user, and approved membership. Stop before opportunity lookup if tenant scope is missing
   or mismatched.
4. Resolve one opportunity by ID or unambiguous search. Confirm the requester is the owning
   AE when ownership materially affects access or the framing of actions.
5. Require a non-empty `get_opportunity` payload whose `id` and opportunity citation match
   the selected ID. Compare `current_context.user.id` with `owner_id`; when they differ,
   require explicit on-behalf-of framing or route a manager-led request to `$deal-review-prep`.
6. Use only read-only calls. Never create notes, update CRM fields, draft or send messages,
   create interventions, or invoke approval-gated actions.

## Gather the minimum evidence

Use logical capabilities only when exposed and permitted:

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
| `risk_heatmap` | Optional portfolio response: page and select the exact opportunity ID locally, disclose coverage, and treat bounded-page absence as unavailable |

Retrieve bounded results sufficient for the inspection horizon. Disclose truncation. Do not
pull a broad account or team review merely to fill the page.

The live methodology asset may identify `MEDDPICC` while the summary capability accepts
`MEDDPIC`. Use only a token explicitly supported by the live capability, label that analysis
**Partial — Competition component unavailable**, and never present the seven-component result
as full MEDDPICC completion. Reconcile any signal-recommended actor with the authoritative
opportunity owner; suppress a named assignment when they differ.

## Prepare the inspection pack

1. **Snapshot:** State current deal facts and source freshness. Keep tool-provided scores
   separate from model judgment; follow the response's score semantics.
2. **Rep narrative:** Summarize what has happened in three to five evidence-grounded lines.
   Label notes as authored narrative and activities as observed events.
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
  fixture-marked rows from real counts. When the connector or `current_context` identifies a
  demo, test, or staging deployment and provenance is not reliable on every row, label every
  output exactly:
  **Demo data — not for customer or commercial decisions.**

## Deliver

Default to a one-page in-chat or Markdown inspection sheet with these sections:

- Deal snapshot
- What the evidence says
- Gaps to acknowledge
- Likely questions and answer evidence
- Rep-owned next actions
- Sources and limits

Do not create a PPTX unless the user explicitly requests a personal one-page aid and the
request remains AE-owned. Route any formal pipeline-review or manager-facing deck to
`$deal-review-prep`.

## Verify before delivery

- The organization, opportunity, and owner are unambiguous.
- Every claimed fact is cited and freshness is visible.
- Each proposed answer distinguishes known evidence from unknowns.
- No timeline dispute was handled here instead of `$deal-timeline-defence`.
- No manager-led formal review was handled here instead of `$deal-review-prep`.
- Fixture evidence is excluded from real counts and labelled when present.
- No CRM write, email action, intervention mutation, or approval-gated action was called.
