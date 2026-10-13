---
name: "rep-coaching-report"
description: "Prepare an evidence-based Summit53 coaching deck (PPTX) for a routine developmental 1:1 with a sales rep, built around one Results/Effort/Knowledge/Skills coaching thesis from the stored diagnostic, call behaviour, coaching history, pipeline, deal risk, MEDDPICC gaps and activity. Also handles explicit post-session capture of notes, agreed actions or a later outcome when that capability is exposed and approved. Trigger on 'prep my 1:1 with [rep]', 'what should I coach [rep] on?', 'coaching report for [rep]', 'build a coaching deck', 'what's going on in [rep]'s pipeline before our 1:1', 'log my notes from the session with [rep]', 'close out the [rep] 1:1' or 'record the action items from my coaching session'. Do not use for promotion, PIP, calibration or HR decisions — use rep-evidence-dossier."
version: "2.1.0"
baselined: "2026-10-13"
status: "active"
---

# Rep Coaching Report

Prepare a humane, evidence-based coaching conversation for a routine 1:1, built around
one high-leverage thesis. The output is a PPTX for the rep and their manager. It is not
a formal assessment, and it never makes an employment recommendation.

## Route first

- Promotion, PIP, talent calibration, formal performance review, HR documentation or any
  employment decision → `rep-evidence-dossier`. Stop and route before pulling coaching
  evidence; do not produce this deck for those uses.
- Routine developmental coaching, recurring 1:1 prep, "what should I coach them on?",
  and explicit post-session capture → this skill.
- Closed-deal cohort patterns → `win-loss-analysis`. Territory or segment review →
  `territory-review`.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete
its checklist before any data call. Then apply these coaching-specific gates:

1. **Demo label.** Exclude `synthetic`, `demo_seed` and `demo_fixture` rows from a real
   1:1. A Staging or demo run that uses them carries **Demo data — not for real
   coaching** on every slide.
2. **Load tools in one batch.** One ToolSearch `select:` call covering the read tools in
   [references/workflow-spec.md](references/workflow-spec.md#tools), resolved to the
   connector that passed `current_context`.
3. **Inspect the live schema of every tool before calling it.** As at 2026-10-13 the
   live connector has the shapes below, and the workflow is written against them. If the
   live schema differs, follow it and say so in the run summary.

   | Tool | Argument shape |
   |---|---|
   | `coaching_diagnostic` | scalar `rep_id` (a separate `rep_ids` is the batch form) |
   | `coaching_agenda`, `coaching_history`, `coaching_development`, `coaching_meeting_analytics`, `rep_coaching_context` | scalar `rep_id` |
   | `hunter_farmer_mix` | `window_quarters` only: **no rep argument**. Call at roster level, select `classifications[]` where `user_id` equals the rep's ID |
   | `ramp_cohort` | **no arguments**. Call at roster level, select `reps[]` where `user_id` equals the rep's ID |
   | `risk_heatmap`, `forecast_confidence`, `pipeline_risk_summary`, `deal_drag_dashboard` | `reps: [repId]` |
   | `activity_gaps` | `owner_ids: [repId]` |
   | `team_action_plan` | scalar `user_id` |
   | `deal_drag_summary` | no arguments: **organization-wide**, never rep totals |
   | `search_opportunities` | no owner filter: never use it to resolve or scope a rep |
   | `capacity_to_target_planner` | `group_by: "sales_region"`, `level: "leaf"`: roster-level region context; read warnings and locate the rep's region group (optional) |
   | `get_opportunity` | scalar `opportunity_id`; `sales_team_at_close` only once that field is exposed (pending deploy; optional) |

4. **Resolve the rep from the roster.** Use the `user_id` from
   `coaching_intervention_plan` or another authorized coaching-roster response. If no rep
   is named, show the authorized roster unranked and let the user choose.
5. **Viewer authorization.** Confirm the requester is authorized for this rep's coaching
   record. Do not expose one rep's sensitive evidence to an unauthorized audience.

## References

- [references/workflow-spec.md](references/workflow-spec.md): **read completely before
  the first data pull.** It holds the data pulls and contract-compatibility rules, the
  pattern analysis and causal chain, the slide-by-slide spec, the build and QA steps,
  and the full post-session write conversation.
- [references/structural-confounders.md](references/structural-confounders.md): read
  before attributing any flag, benchmark gap, ramp figure or win rate to the rep. It
  governs flag base rate, P75 meaning, verified-versus-unverified values, segment, ramp
  survivorship and role–motion fit.
- [references/connector-preflight.md](references/connector-preflight.md): the shared
  tenant, schema, fixture, read-only, missing-evidence, correlation and delivery
  contract.

## Workflow overview

Each step is specified in full in
[references/workflow-spec.md](references/workflow-spec.md).

1. **Context and rep.** `current_context`, roster resolution, viewer authorization, and
   the route-out check for formal or HR requests.
2. **Foundation pulls.** `coaching_diagnostic` (the thesis), `coaching_agenda`
   (capture `session_id` and `previous_action_items`), `coaching_meeting_analytics`
   (the highest-leverage pull), `coaching_development`, and `coaching_history` (the
   authoritative delivered-coaching record), with `rep_coaching_context` as the
   resilience fallback. Then the lenses: `revenue_loop_diagnosis`, `hunter_farmer_mix`,
   `ramp_cohort` and `list_methodology_playbooks`. Access-gated lenses are optional.
3. **Deal-level pulls**, in parallel: forecast, `risk_heatmap` with `period_span: 2`
   and a truncation check, rep-scoped pipeline risk, activity gaps, MEDDPICC framework
   summaries, notes, activities, signals, deal drag, action plan, and optional outreach
   and renewal blocks.
4. **Analyse.** Ten pattern checks, a causal chain whose every link is evidenced, the
   fairness checks, and 3–5 specific recommendations. On-target reps get a short,
   honest deck.
5. **Build the deck** with PptxGenJS following the `pptx` skill, using the Midnight
   Executive slide spec (Slides 1–10, with optional 2b, 2c, 4b and 8b).
6. **QA and deliver.** Render every slide, inspect each at full size, fix defects, and
   return one clickable link with a short note on evidence gaps.

## Guardrails

- **Report generation is read-only.** Never pass `refresh: true` and never write while
  preparing the deck.
- **One thesis, kept as a hypothesis.** Keep facts, Summit53 model outputs, coaching
  hypotheses and agreed actions visibly distinct. A mechanism is a hypothesis to test in
  the room, not a proven fact.
- **No ranks or named comparisons.** Honour `coaching_flag_quality` and
  `ordering.ordinal_ranking`. Never render "priority #N of M", a leaderboard or a
  named-rep comparison. A non-discriminating flag is a statement about the cohort.
- **P75 is aspirational.** Label team P75 as "an aspirational reference, not a peer
  average". Below P75 does not mean below average. Cite a diagnostic value only when
  `_evidence[metric].verified` is `true`.
- **Coaching history is lifecycle-precise.** Planned is not delivered; delivered is not
  acknowledged; a later outcome is not proof of causation. Intervention-ledger rows are
  deal-execution accountability, never coaching delivered.
- **Unavailable is not zero.** A bare `{}` from `activity_gaps`, an unavailable drag
  analytics block or a missing diagnostic is indeterminate. It is never rendered as
  "all accounts engaged", "no drag" or a green status.
- **Region before team.** Treat sales region and segment as confounders: compare the
  rep within their own sales region or segment before any team-wide comparator, surface
  the region-grouping warnings (`reps_without_team`, `market_quota_unassigned`), and
  attribute closed deals to the team the rep was in at close when `sales_team_at_close`
  is exposed. Region context never becomes a rank or a named-peer comparison.
- **Scope before attribution.** Never attribute an organization-wide figure
  (`deal_drag_summary`, unscoped `quota`, `coverageRatio`, `totalForecast`, `gap`) to
  the rep.
- **Polarity from `score_semantics`**, never from a field name.
- **Correlational language** for every coaching, activity and outcome relationship.
- **Behavioural, forward-looking language.** No identity labels, blame or unsupported
  performance conclusions.

## Post-session write step (summary)

This is a separate, optional workflow after the 1:1. It never runs as a side effect of
report generation. The full conversation (trigger phrases, gathering notes, good action
items, edge cases and what it unlocks) is in
[references/workflow-spec.md](references/workflow-spec.md#step-6-post-session-capture).

- **Capabilities:** `complete_coaching_session` attests and completes a session;
  `record_coaching_outcome` records a later outcome assessment. They are separate
  lifecycle events and each needs its own explicit request.
- **Current connector:** as at 2026-10-13, **neither write is exposed** by the
  connected Summit53 connector (`list_available_tools` lists no coaching write). If the
  capability is not in the live tool list and schema, **do not attempt it.** Produce a
  structured draft of the manager's notes and agreed action items, state clearly that
  nothing was saved, and tell the user to record the session in the product's
  `/coaching` page.
- **If a write is exposed:** require an explicit user request for that specific write,
  the connector's approval flow, and an idempotency key where the schema supports one.
  Verify the session, organization, rep and current status first; never re-complete or
  overwrite a completed session; call once; report only the confirmed saved result.

## Verification

Before delivery:

- [ ] `current_context` ran first; returned IDs match the scoped organization; the rep
      came from the roster and the viewer is authorized
- [ ] Every argument shape matches the live schema (scalar `rep_id`; roster-level
      `hunter_farmer_mix` and `ramp_cohort` filtered locally)
- [ ] `risk_heatmap` was pulled with `period_span` ≥ 2 and `truncated_by_period` is
      `false`
- [ ] No organization-wide figure appears as a rep figure
- [ ] Health and engagement colours follow `score_semantics.direction`
- [ ] `activity_gaps` green callout only for an empty list with scope metadata; a bare
      `{}` is omitted as indeterminate
- [ ] MEDDPICC shows completion and score together, with all eight components or a
      footnote naming the missing one
- [ ] No rank, leaderboard or named-rep comparison; flag quality stated where
      non-discriminating; P75 labelled aspirational; only verified diagnostic values
      cited
- [ ] Every ramp figure carries the survivor-cohort caveat; motion, segment and sales-region
      fairness checks applied before any win-rate comparison; region warnings surfaced or
      region context stated unavailable
- [ ] Coaching-history lifecycle states kept distinct; ledger rows not shown as coaching
- [ ] Causal-chain links each carry a number and a sample size; no causal language
- [ ] Fixture rows excluded, or **Demo data — not for real coaching** on every slide
- [ ] Every slide rendered and inspected at full size: no clipping, overlap, placeholder
      copy, source mismatch, or sensitive-detail leakage (no other rep's data, raw
      errors, tool prefixes or IDs)
- [ ] No write was attempted during report generation; one clickable link returned
