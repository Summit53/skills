# Rep Coaching Report — Workflow Specification

Version 2.1.0 · 2026-10-13. The full workflow behind [../SKILL.md](../SKILL.md). Read it
completely before the first data pull. The shared tenant, schema, fixture, read-only,
missing-evidence and delivery rules live in
[connector-preflight.md](connector-preflight.md). The rules for flags, benchmarks, ramp,
segment and role-fit live in [structural-confounders.md](structural-confounders.md).

## Contents

- [Why this exists](#why-this-exists)
- [Step 1: Context and rep](#step-1-context-and-rep)
- [Step 2: Pull the data](#step-2-pull-the-data)
  - [Contract compatibility (read first)](#contract-compatibility-read-first)
  - [Foundation pulls](#foundation-pulls)
  - [Lenses](#lenses)
  - [Deal-level pulls](#deal-level-pulls)
  - [Handling missing data](#handling-missing-data)
- [Step 3: Analyse patterns](#step-3-analyse-patterns)
  - [Pattern detection](#pattern-detection)
  - [Build a causal chain, not a symptom list](#build-a-causal-chain-not-a-symptom-list)
  - [Fairness checks](#fairness-checks)
  - [Coaching recommendations](#coaching-recommendations)
  - [On-target reps](#on-target-reps)
- [Step 4: Build the deck](#step-4-build-the-deck)
  - [Design system](#design-system)
  - [Slide specification](#slide-specification)
- [Step 5: Generate, QA and deliver](#step-5-generate-qa-and-deliver)
- [Step 6: Post-session capture](#step-6-post-session-capture)
- [Tips for great coaching reports](#tips-for-great-coaching-reports)
- [Tools](#tools)

---

## Why this exists

Sales managers spend hours prepping for 1:1s: pulling deal data, cross-referencing
activity logs, trying to spot patterns. This skill does it in one pass. Live CRM and
coaching data flow into a professional coaching deck with specific, evidence-based
recommendations. It turns data into coaching conversations.

The 1:1 is a ritual, not a hot seat. The deck exists to make one conversation better.
It is not a record for a formal decision; that is `rep-evidence-dossier`.

---

## Step 1: Context and rep

1. Call `current_context` first. Confirm the organization matches the user's intended
   organization before reading any rep evidence. If it does not, stop and ask the user
   to reconnect or confirm the intended context.
2. Resolve the rep through `coaching_intervention_plan` or another authorized
   coaching-roster response. Use the roster-provided `user_id`.
3. Do not infer rep identity from `search_accounts` or `search_opportunities`; neither
   has a reliable rep-name or owner filter.
4. Confirm the viewer is authorized for that rep. Do not expose one rep's sensitive
   evidence to an unauthorized audience.
5. If the request is formal-review, PIP, promotion, calibration, HR or
   employment-decision shaped, stop and route it to `rep-evidence-dossier` before pulling
   coaching evidence.

If the user does not name a rep (or says "just do it"), present only the authorized
coaching roster so they can choose. Do not rank it.

---

## Step 2: Pull the data

Run independent calls in parallel. Argument shapes below match the live schema as at
2026-10-13; inspect the live schema before each first call and follow it if it differs.

### Contract compatibility (read first)

Summit53's scoring and filtering contracts were revised in the framework-scoring release
(migrations 0063/0064). Servers may be running either side of that change, so **read
canonical fields first and fall back to the legacy alias only if the canonical field is
absent**, never the reverse:

| Read this | Legacy alias | Notes |
|---|---|---|
| `healthScore` | `riskScore`, `risk_score` | Canonical is 0–1, `higher_is_healthier`. |
| `contactEngagement` | `contactRisk` | Stakeholder engagement. |
| `activityMomentum` | `activityDrag` | Opportunity activity momentum. |
| `repCommitConfidence` | `repCommitLevel` | Forecast-category commitment confidence. |

**Do not infer polarity from an alias name.** Under the deployed contract
(`score_semantics` v1.2) the aliases carry values *identical* to their canonical targets
(`deprecated_alias_policy.inverted: false`). So `contactRisk: 0.30` means engagement is
0.30 and the deal is weak, despite the name implying the opposite. Read
`score_semantics.direction` and `factor_semantics` and follow them; never colour or
interpret a factor from its field name. Aliases are scheduled for removal in 2.0.0 of
the contract.

Where a response carries `score_semantics`, trust it over anything written here. It
declares `primary_field`, `direction` and the correct `riskiest_first` sort.

Two scope rules stop wrong numbers reaching a slide:

- **Never render an aggregate as rep-scoped unless the response says it is.** Filtered
  responses carry scope metadata; org-level fields (notably `quota`, `coverageRatio`,
  `totalForecast`, `gap`) may be organization-wide even when `reps` was passed. If scope
  is absent or ambiguous, omit the figure rather than attributing it to the rep.
- **Confidence values are not all on one scale.** A response may carry envelope
  confidence (0–1), org confidence and per-rep confidence in different units. Use the
  rep-scoped value for rep-scoped claims and label the scale.

### Foundation pulls

Pull these first; they frame the report.

- **Coaching diagnostic**: `coaching_diagnostic(rep_id: repId)`, scalar. Confirm the
  response is for that rep; if it comes back roster-shaped, select the rep's row
  locally. It returns the diagnosed coaching layer (Results / Effort / Knowledge /
  Skills / `on_target` / `other`), the single focus metric with the highest improvement
  leverage, the gap against the team P75 benchmark, and signal-quality metadata. This is
  the deck's **thesis**: everything else is evidence supporting or nuancing it, and it
  remains a coaching hypothesis, not a verdict about the person. "Rep diagnostic not
  found or unavailable" means no stored diagnostic; say so and build from the
  remaining evidence.
  - **The selection score is not a rank.** `focus_metric_selection_score` (or
    `composite_score` on older builds) chooses between one rep's candidate metrics.
    Check `ordering.ordinal_ranking`; when it is `false`, never sort the team on it or
    render "priority #N of M". Ties are retained deliberately.
  - **Check `coaching_flag_quality` before treating the flag as meaningful.** When
    `classification` is `non_discriminating` (the flag applies to most of the roster,
    for example 17 of 19 reps), being flagged carries almost no information. Say so on
    Slide 2 rather than implying the rep was singled out.
  - **Benchmarks are P75, not peer average.** Quote `benchmark_context.warning` and
    `peer_count`. Frame gaps as distance from an aspirational bar, and never
    characterise a rep at or near quota as an underperformer on a P75 shortfall alone.
  - **Verified values only.** Cite a `results_scores` value only when
    `_evidence[metric].verified` is `true`. Otherwise say the value is not established
    and name the status. A benchmark without a verified rep value is not a gap.
- **Coaching agenda**: `coaching_agenda(rep_id: repId)`. Returns the stored upcoming
  session: `session_id`, `week_type` (Strategic / Skills / Career / Execution / Close),
  `coaching_model`, `scheduled_date`, `diagnostic_summary`, and `previous_action_items`
  carried forward from the last 1:1. **Capture the `session_id`** for Step 6, and the
  `previous_action_items` for Slide 8. If it returns "No active coaching cadence found"
  or `status: "not_generated"`, skip the agenda-dependent sections (session footer,
  previous action items) and continue. A stored agenda is never evidence that coaching
  was received.
- **Meeting analytics**: `coaching_meeting_analytics(rep_id: repId, weeks: 13)`.
  Returns per-call behavioural measures (`question_rate_per_min`,
  `longest_monologue_sec`, `interactivity_per_min`, `talk_ratio`) and flagged sessions.
  **This is the highest-leverage pull in the skill and must not be skipped.** Dashboard
  metrics say *what* is off; these say *what the rep is actually doing in the room*,
  which is the only thing a manager can coach directly. A rep at 0.1 questions/min with
  a six-minute longest monologue is consistent with thin qualification, absent
  economic-buyer access and a low win rate, none of which is visible from the diagnostic
  alone. Where the diagnosed metric and the call behaviour point at the same root cause,
  lead with the behaviour: it is observable, rehearsable and upstream. Where
  `total_meetings` is 0, call behaviour is unavailable, not neutral.
- **Development**: `coaching_development(rep_id: repId)`. Stored development goals with
  `progress_pct`, the 13-week diagnostic history and the `focus_metric_trend`. It gives
  trend context but does not establish that coaching was delivered.
- **Coaching history**: `coaching_history(rep_id: repId)`. The **authoritative
  delivered-coaching record**: recommendations, plans, scheduled and completed sessions,
  manager attestations, notes, actions, acknowledgements and later outcome assessments.
  Read each row's lifecycle state. A recommendation, plan or scheduled session is not a
  completed coaching receipt. A completed receipt documents support delivered; it does
  not prove acknowledgement, persistence or outcome. Assigned deal interventions come
  back separately (`include_assigned_interventions`) and never count as coaching. Inspect
  provenance and exclude `synthetic`, `demo_seed` and `demo_fixture` rows from a real
  coaching deck.

**Aggregate fallback:** `rep_coaching_context(rep_id: repId)` returns diagnostic,
development, history (`history_limit` 1–50), meeting analytics and agenda in one call.
Use it when the granular calls are refused: `coaching_history` in particular has
returned "No approval received" intermittently where the aggregate succeeded. Prefer the
granular calls when they work, treat the aggregate as the resilience path, and label the
fallback. If the two disagree, use the granular value and note it.

### Lenses

Pull these to cross-validate and contextualise the diagnosis before deal-level
evidence. All are manager- or team-permission gated: on an authorization error or a
`requires_manager_role` warning, skip that lens gracefully (omit its callout on Slide 2)
and continue. Don't block the report on them.

- **Revenue loop diagnosis**: `revenue_loop_diagnosis`. Its coaching lane names a
  priority rep and a failing layer by a different signal path from
  `coaching_diagnostic`. If it agrees with the diagnosed layer for this rep, that is
  corroboration; say so on Slide 2. If it disagrees, surface the tension rather than
  silently trusting one signal. If its priority rep is someone else, note only that the
  loop prioritises a different rep this week; do not name them.
- **Hunter/farmer mix**: `hunter_farmer_mix(window_quarters: 4)` at roster level; select
  the `classifications[]` row whose `user_id` equals `repId`. Do not pass a rep argument
  (the schema has none). Shares are numeric on current builds; older builds return
  high-precision decimal strings (including forms like `"0E+2"`), so coerce and round to
  whole percentages before rendering. `unknown` (below the closed-won threshold) means
  role-fit could not be assessed, never "no mismatch".
- **Ramp cohort**: `ramp_cohort` at roster level (no arguments); select the `reps[]` row
  whose `user_id` equals `repId`. Relevant for newer reps only. A rep absent from
  `reps[]` is not in a current ramp window; an empty payload with a
  `requires_manager_role` warning means ramp status could not be established. **Survivor
  cohort:** `ramp_cohort` covers only reps currently in their ramp window and excludes
  everyone who left during ramp, so the cohort curve is biased optimistic. Wherever a
  ramp figure appears, state n and use the wording and n-thresholds in
  [structural-confounders.md](structural-confounders.md) Screen 3 (at n = 1, show no
  cohort median: it is the rep's own number).
- **Region context** (optional enhancement):
  `capacity_to_target_planner(group_by: "sales_region", level: "leaf")` at roster level.
  It places sellers in leaf Sales Org region groups. Use it for two things only:
  - **The rep's region group**, as the context for comparisons. Locate the planning group
    that contains `repId` in the live response. If the response is `insufficient_data`,
    falls back to a single blended group (check `data_quality.group_by` and
    `grouping_strategy`), or the rep is not in any group, region membership is **not
    resolved**: say so and do not guess a region from accounts or opportunities.
  - **Grouping warnings, surfaced as confounders.** `reps_without_team` (if it includes
    this rep, region comparison cannot be made for them), `market_quota_unassigned`,
    `region_grouping` and `owner_profile_attribution` change what any region figure means;
    quote them in Slide 2's speaker notes and as a muted line where they bear on a
    comparison.
  Never present a region's quota, capacity or gap as the rep's figure, and never list
  other reps from the group's contributors. Where `segment_performance_summary(dimension:
  "sales_region", level: "leaf")` is exposed and permitted (it needs analytics
  permission), the rep's region row is the like-for-like comparator for win rate and cycle
  time; otherwise the comparator stays "team, all segments" and is labelled so.
- **Team at close** (pending deploy; optional): once `get_opportunity` exposes
  `sales_team_at_close{id, name, team_type, source}` (null while a deal is open), read it
  for the closed deals cited in the deck and attribute each to the team the rep was in at
  close, not their current team. This matters for a rep who moved teams: their closed-won
  history belongs to the earlier region's comparator. If the field is absent from the live
  schema, skip it and note in the run summary that closed deals were attributed to the
  current team assignment. Never use `search_opportunities` to scope a rep's closed deals.
- **Methodology playbooks**: `list_methodology_playbooks`. The org's own published
  MEDDPICC or BANT definitions, "what good looks like" per element in the org's own
  language. This grounds Slides 5 and 6.

### Deal-level pulls

Run these in parallel once the rep is resolved.

1. **Pipeline and forecast**
   - `forecast_confidence(reps: [repId])`: confidence, deal count, pipeline value,
     velocity, coverage (rep-scoped fields only).
   - `forecast_confidence` unfiltered: team comparator. It spans segments and motions,
     so label it accordingly.
2. **Deal risk heatmap**
   - `risk_heatmap(reps: [repId], page_size: 25, period_span: 2)`: every deal with
     health, framework scores and risk factors.
   - **`period_span` is mandatory.** The default covers one quarter and silently
     truncates a rep's book. A rep with deals spanning two quarters returned 5 of 16
     deals on the default, understating pipeline by two thirds with no warning.
   - **Check `scope_summary` on every response** (`matching_open_total`,
     `in_period_total`, `out_of_period_total`, `truncated_by_period`). If
     `truncated_by_period` is `true`, widen `period_span` and re-pull before building
     anything. Never build a deck on a truncated set.
   - **Sorting:** riskiest-first is `healthScore` ascending (the default). Follow
     `score_semantics.riskiest_first`. Never sort `riskScore` descending: against a
     canonical server that returns the *healthiest* deals first.
3. **Pipeline risk distribution**
   - `pipeline_risk_summary(reps: [repId], period_span: 2)`.
   - **Use only rep-scoped fields:** `byRep`, `repMetrics`, `totalDeals`,
     `byRiskLevel`, `velocityMetrics.stuckDeals`. Check scope metadata before using
     anything else.
   - **Never attribute `quota`, `coverageRatio`, `totalForecast` or `gap` to the rep**
     unless scope metadata confirms they are filtered. On older builds they stay
     organization-wide even when `reps` is passed; a $27.5M quota on a single rep's
     slide is the failure this guards against. If in doubt, omit.
4. **Activity gaps**
   - `activity_gaps(days: 30, owner_ids: [repId])`: the rep's accounts with no recent
     engagement.
   - The canonical response is a list with scope metadata, so an **empty list with
     scope metadata** genuinely means no gaps. Older builds can return a **bare `{}`**:
     treat that as **indeterminate**, not as good news, and omit the slide's all-clear
     rather than asserting "all accounts engaged".
5. **Framework analysis** (MEDDPICC by default)
   - For each of the rep's top deals (up to 8–10 from the heatmap), call
     `opportunity_framework_summary` with `framework: "MEDDPIC"` and the opportunity ID.
     These calls are independent; run them in parallel.
   - **`"MEDDPIC"` is the stable database key** and is correct as the argument. It is
     not a typo and must not be "corrected" to `"MEDDPICC"`.
   - The canonical component set is **eight**: Metrics, Economic Buyer, Decision
     Criteria, Decision Process, Paper Process, Identified Pain, Champion,
     **Competition**. Older builds return seven (no Competition) and call Identified Pain
     "Implicate Pain". Reconcile against `list_methodology_playbooks`; if the served
     component count is below the playbook's, say so on Slide 5 rather than reporting a
     deal as fully qualified against a partial model.
   - **Completion is not competence.** `completion_percentage` measures whether fields
     are populated; component scores measure whether the evidence behind them is real.
     A book at 100% complete and 50% scored is a qualification-depth problem, not a
     CRM-hygiene problem, and the coaching differs completely. Always report both
     numbers together; never report completion alone.
   - SPICED and Three Whys are scored independently of MEDDPICC. Do not treat a zero on
     one as a gap in another; check whether the org uses that framework first.
6. **Deal narratives** (parallel with framework analysis)
   - `get_opportunity_notes_summary` for the same top deals.
   - `get_opportunity_notes` for the top 3–5 risk deals: unresolved blockers and
     objections.
   - `get_opportunity_activities` for the top 3–5 risk deals: cadence and last touch.
   - `get_opportunity_signals` for the top 2–3 risk deals: the single first-constraint
     (the primary blocking factor Summit53's signal engine identifies) as a one-line
     talking point on Slide 4.
7. **Deal drag**
   - `deal_drag_dashboard(reps: [repId])`: waste scores, staleness, activity level,
     drag cause (political / technical / commercial / process) and recovery strategies.
     This is the "cost of inaction" layer: a rep can look fine on health scores and still
     have $500K sitting dark for 30+ days. Compute the rep's stalled count, stalled value
     and average waste score from these rows.
   - `deal_drag_summary` takes no arguments and is **organization-wide**. Use it only as
     a labelled team comparator, never as the rep's totals.
   - **Analytics blocks may be explicitly unavailable.** Drag causes, recovery
     strategies and scenario detections can return an unavailable marker. Omit those
     elements when unavailable; an empty or zeroed analytics block is not "no drag
     causes exist".
   - **Deal drag and `pipeline_risk_summary` band deals on different constructs** (waste
     versus health) and will legitimately disagree. Present both with their basis named
     rather than picking a winner: a manager seeing "0 stalled" on one slide and
     "3 stuck" on another with no explanation will distrust the whole deck. Cross-check
     `stalled_deals_count` against `activity_breakdown` within the same response; if they
     disagree, trust the activity breakdown and note the discrepancy.
8. **Action plan and accountability**
   - `team_action_plan(user_id: repId)`: action completion, missed deadlines, flagged
     items. This is deal-execution accountability, distinct from coaching commitments.
9. **Outreach health** (optional; include only if the rep manages outreach leads)
   - `outreach_funnel_summary` and `search_outreach_leads` scoped to the rep where the
     live schema offers an owner filter. If it does not, omit rep-level outreach claims.
10. **Renewal and expansion signals** (optional; include if the org tracks post-sale
    value)
    - `list_account_contracts` for the rep's top-value accounts, then
      `list_impact_entries` for those contracts.

### Handling missing data

Don't fail if data is sparse; adapt.

- If framework summaries fail for some deals, skip them and note "Framework data
  unavailable" for those deals.
- `activity_gaps`: an empty **list with scope metadata** is a genuine positive ("No
  engagement gaps detected"). A bare empty object, or a payload without scope metadata,
  is indeterminate: omit the claim. An empty payload cannot be distinguished from a
  failed query, and rendering a silent failure as good news is worse than saying
  nothing.
- Distinguish "measured and healthy" from "not measured" throughout. Where a response
  marks an analytics block unavailable, say the data isn't available rather than
  reporting zero. A manager acting on a fabricated zero is the failure this prevents.
- If the rep has very few deals, the deck will be shorter but still valuable.
- If an optional tool is unavailable or unauthorized (for example `list_interventions`
  on a production tenant, or a permission-gated lens), omit that callout gracefully and
  keep building. Do not surface raw errors to the manager. Missing coaching history,
  fixture filtering and organization scope are never silently omitted: label them.

---

## Step 3: Analyse patterns

Before building slides, synthesise the raw data into coaching insights. This is what
makes the report useful: not just numbers, but patterns and recommendations.

### Pattern detection

1. **Framework gaps.** Across the rep's MEDDPICC scores, which elements are consistently
   weak? If 5 of 7 deals score below 50% on Paper Process, that is a coaching priority.
2. **Risk concentration.** Is the rep's risk skewed toward one type (mostly "No
   Champion", mostly "Budget Uncertainty")?
3. **Activity patterns.** Dormant accounts with active deals are a red flag. Use
   `get_opportunity_activities` on the highest-risk deals: if the last activity on a
   Commit-stage deal was three weeks ago, it belongs in the conversation.
4. **Qualitative themes from notes.** Scan notes summaries for recurring themes:
   - pricing objections or procurement resistance across several deals;
   - the same competitor showing up in several deals;
   - stalled next steps ("next step is to schedule X" in old notes with no follow-up);
   - single-threaded deals (notes reference only one contact);
   - paper-process issues raised but unresolved.
5. **Deal health distribution.** What share of deals sit in each health band, and how
   does that compare with the team (labelled as a cross-segment comparator)?
6. **Deal drag and staleness.** How many of the rep's deals are stalled versus low,
   medium or high activity? Average waste score versus the team comparator? Deals in
   Negotiation or Proposal with high staleness? Note the drag cause where available.
7. **Pipeline balance.** Is the rep over-indexed on a few large deals or diversified?
   Check account concentration too: several deals against one account is a different
   exposure from several deals across several accounts.
8. **Ramp context (newer reps only).** If the rep is in `ramp_cohort.reps[]`, check
   whether apparent gaps are normal ramp-stage variance before recommending a fix.
   Remember the cohort is survivor-biased.
9. **Call behaviour.** From `coaching_meeting_analytics`, examine
   `question_rate_per_min`, `longest_monologue_sec`, `talk_ratio`,
   `interactivity_per_min` and flagged sessions. A low question rate with long
   monologues means the rep is presenting rather than discovering, and that behaviour is
   associated downstream with thin qualification, missing Metrics and Economic Buyer, low
   stakeholder engagement and a depressed win rate. Check the sample size: two flagged
   calls is a signal worth raising, not a verdict, and should be framed that way.
10. **Coaching recurrence.** From `coaching_history` and `coaching_development`: has
    this rep been coached on the current focus metric before, and did
    `focus_metric_trend` move afterwards? Note the modality used and whether follow-ups
    were completed. Prior documented coaching with no later movement is the strongest
    evidence in the report, and the clearest instruction not to repeat the same
    approach. Movement after coaching is associated timing, not causation; name the
    baseline and later window.

### Build a causal chain, not a symptom list

The diagnostic names a metric. That metric is usually **where a problem surfaces, not
where it starts**. Before writing recommendations, try to connect the evidence into a
chain from observable behaviour through to outcome. For example: low question rate →
shallow qualification → no economic-buyer access → low win rate, with the diagnosed
metric appearing partway along as a consequence rather than the origin.

The chain is a **coaching hypothesis** to test in the room, not a proven mechanism.
Three rules:

- **Each link must be independently evidenced.** If you cannot cite a specific number
  for a link, it doesn't go in the chain. A plausible story with an unevidenced middle
  is worse than a shorter honest one.
- **Coach the earliest link you have evidence for.** It is usually the most observable
  and the most rehearsable. Coaching the terminal metric (the one on the dashboard)
  tends to produce compliance rather than change, which is exactly the pattern that
  shows up as repeated coaching with a flat trend line.
- **Write it correlationally.** "Is associated with", "sits upstream of", "coincides
  with". Never "caused" or "proves".

Also separate **performance** from **conversion** before framing anything. A rep can be
at quota, faster than benchmark and above benchmark on coverage while still converting
poorly. Those are different conversations, and leading with a "gap" framing on a rep who
is hitting their number will lose the room in the first minute.

### Fairness checks

Run these before any comparison reaches a slide. Each one changes what a number means.

- **Flag base rate.** A non-discriminating flag is a statement about the cohort, not the
  rep. Say how many reps carry it.
- **P75 is aspirational.** Below P75 is the normal state for roughly three quarters of
  any team. Render the gap as a magnitude; under 10% is close to the bar.
- **Verified values only.** Unverified diagnostic values are "not established", never
  zero.
- **Motion.** A pure hunter carries no renewal base, and renewals close at high rates by
  definition. Comparing a 100%-new-business rep's win rate with a teammate whose
  closed-won is mostly renewal is not like-for-like. Where the mix differs materially,
  compare against the same motion and say which comparison you used. "Lowest win rate on
  the team" without that caveat is technically true and substantively misleading.
- **Segment, territory and sales region.** A team comparator spans segments and regions;
  label it. Where the rep's sales region (from the region-context lens) or segment is
  resolved, compare within that region or segment first and only then against the team,
  saying which comparator each figure uses
  ([structural-confounders.md](structural-confounders.md) Screen 2). Attribute closed
  deals to `sales_team_at_close` where exposed. A rep in `reps_without_team`, or an
  unresolved region, gets the team comparator with that caveat, never a guessed region.
- **Ramp.** Ramp figures carry the survivor-cohort caveat and n.
- **Sample size.** State n for every call-behaviour claim and every "X of Y deals".

### Coaching recommendations

Generate 3–5 specific, actionable, behavioural recommendations. Each should:

- reference specific evidence ("4 of your 6 deals have no identified economic buyer");
- suggest a concrete action ("in your next call with Acme Corp, ask who signs the PO");
- connect to the business outcome it is associated with in this book ("the three
  deals without an economic buyer are the three that have sat in Stage 4 longest"),
  without claiming it predicts or causes the outcome.

Avoid generic advice like "improve discovery calls". Ground everything in the rep's
actual data. If documented coaching already addressed the same gap without later
movement, propose a different approach rather than repeating it.

### On-target reps

If `coaching_diagnostic` returned `diagnosed_layer` as `on_target` or `other`, the rep
has no coaching gap this week. Adapt the deck rather than fabricating issues:

- **Shorten aggressively.** A 3–4 slide deck beats a 10-slide one padded with invented
  problems.
- **Slide 2** leads with positive reinforcement: "[Rep] is on-target across all four
  coaching layers this week". Keep the pipeline snapshot and session footer.
- **Slides 3 and 4** still render; on-target reps benefit from a pipeline review too.
- **Slides 5 and 6** collapse into one "Framework strengths" slide calling out the
  strongest MEDDPICC elements.
- **Slide 8** becomes "What's working": 2–3 specific things the rep is doing well, with
  evidence. Keep previous action items if present.
- **Slide 9** becomes "Maintain momentum": 2–3 forward-looking suggestions (expansion,
  stretch goals, areas to deepen).

The goal is honest positive feedback grounded in data, not an empty deck and not a
fabricated critique.

---

## Step 4: Build the deck

Build with the host's presentation toolchain; load it per
[host-adapters.md](host-adapters.md#building-slides) before writing code. Set the 16:9
layout before adding slides, put sources in speaker notes, keep charts native, and build
a structured deck with a theme, layouts and sections. When building with PptxGenJS
(Claude's pptx skill), never use `#` in hex colours, build fresh option objects per call,
and use `addNotes` for speaker notes.

### Design system

**Midnight Executive**, for visual consistency across Summit53 deliverables.

| Role | Colour | Hex |
|---|---|---|
| Primary (dark backgrounds) | Navy | `1E2761` |
| Secondary (light text, accents) | Ice Blue | `CADCFC` |
| Accent (highlights, healthy) | Emerald | `10B981` |
| Warning | Amber | `F59E0B` |
| Danger | Red | `EF4444` |
| Text on dark | White | `FFFFFF` |
| Text on light | Charcoal | `1E293B` |
| Light background | Off-white | `F8FAFC` |
| Subtle border / divider | Slate | `64748B` |
| Light slate (dividers, grid) | Light Slate | `E2E8F0` |

- **Typography:** Cambria headings (36–44 pt) and Calibri body (14–16 pt). Both render
  true-to-width in QA; Georgia does not, so avoid it unless the user asks for it.
- **Layout:** 16:9. At least 0.5" margins. Dark title and closing slides, light content
  slides.
- **Callouts and status:** use a tinted card background, a small coloured status dot or
  an icon in a coloured circle. Do not use left-edge colour bars, single-side borders or
  accent stripes.
- **Colour is for deal and data health, never a rating of the person.** Every
  health-coloured cell follows `score_semantics.direction` (see Slide 4).
- **Helpers:** define small factory helpers (`addStatCard`, `addSectionTitle`,
  `healthColor`, `formatCurrency`). `healthColor` must be polarity-aware: a helper that
  hard-codes "high is red" inverts every canonical health score.
- **Footer on every content slide:** "Coaching 1:1 · {Rep} · {date} · Summit53" and,
  where required, **Demo data — not for real coaching**.
- **Speaker notes:** a short `[Sources]` block per slide naming the logical tools, the
  as-of time and windows, and any fallback or unavailable source.

### Slide specification

Build these slides in order. The deck is designed for a roughly 20-minute 1:1. Optional
slides (2b, 2c, 4b, 8b) render only when their evidence exists; the core conversation
stays near 10 slides.

#### Slide 1: Title

- **Background:** Navy.
- **Content:** "[Rep Name] — Coaching Report", date, "Powered by Summit53".
- **Layout:** centred, clean. Large Cambria title, Calibri subtitle.

#### Slide 2: Coaching diagnosis — this week's focus

- **Background:** Off-white.
- **Data:** `coaching_diagnostic`, `coaching_agenda` (session context),
  `forecast_confidence` (supporting stats), `revenue_loop_diagnosis`,
  `hunter_farmer_mix` and `ramp_cohort` (lenses, if authorized).
- **Purpose:** the thesis of the deck. Every later slide supports or nuances it.

**Top half: the diagnosis.**
- A large centred badge for the diagnosed layer. Colours: amber for `effort`,
  navy-on-ice-blue for `knowledge`, a purple variant for `skills`, red for `results`,
  emerald for `on_target`, slate for `other`. The badge names the layer; it is not a
  severity rating of the rep.
- Below it, the focus metric in readable form (`action_plan_completion` → "Action plan
  completion") with current value, benchmark and gap on one line: "Currently 43%, team
  P75 76% (n=19), gap 43.6%". Add "Team P75 is an aspirational reference, not a peer
  average." Show the value only if it is verified.
- To the right, a **flag-quality callout, not a rank.** Never render "Coaching priority
  #N of M". Where `coaching_flag_quality.classification` is `non_discriminating`, say so:
  "Not a ranking — 17 of 19 reps carry a flag this week." This tells the manager how
  much weight the flag deserves.
- Directly below, a one-sentence hypothesis framed as leverage, not standing: "The
  highest-leverage metric to work on this week is action-plan completion." Not: "[Rep]
  is the team's 3rd-highest coaching priority."
- **Loop cross-check** (if `revenue_loop_diagnosis` was pulled): if it agrees on the
  failing layer for this rep, add a small "confirmed by loop diagnosis" tag. If it
  disagrees, add a slate callout (a data tension, not a risk) stating both readings:
  "Revenue-loop diagnosis reads this as Effort; the coaching diagnostic reads Results.
  Worth exploring both in conversation." Skip entirely if unavailable.
- **Motion lens** (if `hunter_farmer_mix` was pulled): a small inline note, e.g.
  "Natural motion: hunter-leaning (72/28)". Apply the motion fairness check before any
  win-rate comparison. If the layer is `results` and the rep's motion mismatches the
  territory, add: "Consider whether this is a skill gap or a role-fit/territory
  mismatch." If the classification is `unknown`, say role-fit could not be assessed.
- **Region context** (if the region-context lens resolved the rep's group): a small inline
  note, e.g. "Sales region: ANZ Mid-Market (leaf); comparisons below are within region
  where marked". If grouping warnings apply to this rep (for example `reps_without_team`),
  say region comparison was not possible. Never show a region rank or other reps' names.
- **Ramp context** (if the rep is in `ramp_cohort.reps[]`): a muted note, "[Rep] is in
  month N of ramp; current metrics are tracking within X% of expected cohort pace",
  followed by the survivor-cohort caveat and n.

**Bottom half: pipeline snapshot (supporting context).**
- Four compact stat cards, visibly smaller than the diagnosis block: total pipeline
  value, active deal count, forecast confidence (with its scale), average deal size.
- Under each, the team comparator labelled "team, all segments" (or "region" when a
  region-scoped comparator was available). Colour emerald, amber or red only when the
  comparator is like-for-like (same segment or region, and motion); otherwise use a
  neutral fill.

**Session footer** (small, muted, bottom-right): if `coaching_agenda` returned a
session, "Next 1:1 · Week N · {week type} · {coaching model} model · scheduled {date}".

If `diagnosed_layer` is `on_target` or `other`, skip the gap framing and lead with an
emerald positive callout (see [On-target reps](#on-target-reps)).

#### Slide 2b: Outreach health (optional)

- Render only if the rep has measurable outreach-lead responsibility and the data is
  rep-scoped.
- **Data:** `outreach_funnel_summary`, rep-scoped `search_outreach_leads`.
- **Layout:** four stat cards (total leads; created → engaged → qualified → converted)
  and conversion velocity ("8 qualified this period, 2 converted = 25%"), then a bar
  chart or table of stage distribution.
- Below the team comparator, an amber callout: "Lead conversion is trailing the team.
  Review the qualification criteria together." At or above, an emerald callout: "Lead
  conversion is on pace."

#### Slide 2c: The mechanism (include whenever a causal chain is evidenced)

- **Background:** Off-white.
- **Data:** `coaching_meeting_analytics`, aggregated `opportunity_framework_summary`,
  `risk_heatmap` engagement factors, `coaching_diagnostic`.
- **Purpose:** turn the diagnosis from a metric into an explanation. It is usually the
  most useful slide for the manager, because it names something the rep can change on
  Monday.
- **Layout:** 3–4 numbered link cards down the slide, each with a one-line claim and its
  supporting figure. Tint the cards by strength of evidence (red tint for the strongest,
  amber for supporting). Close with one bold line contrasting where the problem
  *surfaces* with where it *starts*, labelled as a hypothesis to test.
- **Rules:**
  - Every link carries a number from the data. No unevidenced links, however well the
    story flows.
  - Name the sample size on call-behaviour claims ("across two captured calls"). Don't
    imply a pattern from thin data.
  - If the evidence doesn't chain, **skip this slide**. A three-link chain with a
    fabricated middle is worse than no slide.
- Include the rep's verbatim qualification language where it is revealing. A champion
  described as briefing an executive on the rep's behalf is concrete evidence of
  single-threading, and lands harder than a score.

#### Slide 3: Deal portfolio health

- **Background:** Off-white.
- **Data:** rep-scoped `pipeline_risk_summary`, `risk_heatmap`.
- **Layout:** three tinted stat cards for deals in each health band (low, medium, high
  health), then a doughnut of the rep's distribution beside the team distribution if
  available (labelled as a cross-segment comparator).
- Add the average health score as a callout, with its scale and direction ("0.58 on a
  0–1 scale; higher is healthier").

#### Slide 4: Deal-level risk detail

- **Background:** Off-white.
- **Data:** rep-scoped `risk_heatmap` and `deal_drag_dashboard`,
  `get_opportunity_notes_summary`, `get_opportunity_notes` and `get_opportunity_signals`
  for the top risk deals.
- **Layout:** a table of the rep's deals with columns Deal, Amount, Stage, Health,
  Framework score, Stakeholder engagement, Days since last touch. Sort weakest-first per
  `score_semantics.riskiest_first`. Cap at 10 rows. Header row navy with white text.
- **Colour follows polarity, and polarity depends on which field the server returned.**
  Under the canonical contract every one of these is `higher_is_healthier` on 0–1:
  emerald ≥ 0.65, amber 0.50–0.64, red < 0.50. If the server returned legacy `riskScore`
  on a 0–100 inverted scale, the bands invert: red ≥ 70, amber 40–69, emerald < 40.
  **Determine which you have before colouring**: read `score_semantics.direction`; never
  guess from the number. Colouring a 0.30 engagement score green because it looks like
  "low risk" is the easiest way to turn a severe finding into a reassuring one.
- Include stakeholder engagement whenever available. It is often the most revealing
  column and the most commonly misread: under the canonical contract a low value means
  *weak engagement*, not *low risk*.
- **Deal narratives** below the table: for the top 3 highest-risk or highest-waste
  deals, a one-line excerpt from the notes summary.
- **Blockers requiring action** (amber-tinted callout): from the latest notes on the top
  3–5 risk deals, 2–3 unresolved objections, stalled next steps or unaddressed
  commitments, with dates: "Pricing objection on Acme (noted 5 days ago): plan the
  escalation call together." Where `get_opportunity_signals` returned a first-constraint
  for one of the top 2–3 risk deals, lead with it: "Champion risk is the blocking
  constraint on Acme; the pricing objection noted 5 days ago compounds it." Otherwise use
  the notes-derived blocker alone.

#### Slide 4b: Deal drag analysis

- **Background:** Off-white.
- **Data:** rep-scoped `deal_drag_dashboard`; `deal_drag_summary` only as a labelled
  organization comparator.
- **Layout:** three stat cards computed from the rep's dashboard rows: stalled deal count
  (red tint if > 0), pipeline value stalled, average waste score (against the labelled
  organization comparator).
- For each stalled deal (`activity_level: "stalled"`), a card with deal name and amount,
  days since last activity, and:
  - the drag cause tag (political / technical / commercial / process), **only if the
    drag-cause analytics are available**. If the block is marked unavailable, omit the
    tag rather than rendering a default or a zero;
  - the dashboard's recovery action, under the same rule. If recovery strategies are
    unavailable, drop the line; never substitute a generic action of your own and
    present it as system-derived.
- Frame stalled deals as "revenue that has stopped moving".
- An emerald "No stalled deals — all pipeline is active" callout appears **only when
  staleness was actually measured**. Cross-check `activity_breakdown` and
  `pipeline_risk_summary.velocityMetrics.stuckDeals` first; if they show dormant or stuck
  deals while the stalled count reads zero, present both with their basis named instead
  of a green all-clear the rest of the deck contradicts.

#### Slide 5: MEDDPICC framework analysis

- **Background:** Off-white.
- **Data:** aggregated `opportunity_framework_summary`, `list_methodology_playbooks`.
- **Headline the completion-versus-score gap.** If the book is near 100% complete but
  scores materially lower, that contrast *is* the slide's message. It reframes the
  conversation from "fill in your CRM" to "your qualification evidence is thin".
- **Layout:** a horizontal native bar chart or table of the eight elements (Metrics,
  Economic Buyer, Decision Criteria, Decision Process, Paper Process, Identified Pain,
  Champion, Competition) with the rep's average score across deals.
  - If the server returns seven components, render seven and footnote the missing one.
    Never present a partial model as complete.
  - Bars: emerald ≥ 70%, amber 40–69%, red < 40%.
  - Beside each element, how many deals scored below 50% ("Paper Process — 5/7 deals
    below 50%").
  - Under each element name, the org's own one-line definition from
    `list_methodology_playbooks`, so "what good looks like" is the org's published
    standard. If the playbook returns nothing for the framework, use the standard
    element names without definitions.
- If a chart is awkward, use a clean table with tinted cells.

#### Slide 6: Weakest framework areas (deep dive)

- **Background:** Off-white.
- **Data:** `opportunity_framework_summary` for the 2–3 weakest elements.
- **Layout:** one card per weak element, listing the deals where it is weak with the
  score and what specific evidence is missing.
- This gives concrete talking points: "On Acme we don't have a champion identified yet.
  What's your plan?"

#### Slide 7: Activity and engagement patterns

- **Background:** Off-white.
- **Data:** `activity_gaps`, `get_opportunity_activities` (top 3–5 risk deals).
- **Layout:** if dormant accounts exist, an amber-tinted callout with the count, then a
  table of account, days since last activity, and any active deal value at risk.
- **Deal cadence:** for the highest-risk deals, deal name, last activity date, activity
  type and days since last touch. Flag any Commit or Negotiation deal with no activity
  in 14+ days with a red status dot.
- **All-clear rule:** a green "All accounts engaged" callout appears **only when the
  response was an empty list carrying scope metadata**, confirming the query ran and
  found nothing. If the payload was a bare `{}`, show nothing in its place, or a muted
  "Engagement gaps could not be determined from this response". You cannot tell a clean
  book from a failed query, and green-lighting the latter is worse than leaving the
  space blank.

#### Slide 8: Coaching recommendations

- **Background:** Off-white.
- **Data:** `coaching_history`, `coaching_agenda.previous_action_items`,
  `team_action_plan`, and the synthesised recommendations.
- **Layout**, top to bottom:
  1. **Previous coaching commitments**: `previous_action_items` from the agenda, which
     are the actions recorded when the last session was completed. Each has a `task` and
     a `completed` flag; render a short checklist with an emerald check for completed
     and an amber open circle for outstanding. Show only actions carried from an
     attested or completed session; if any item is excluded on that basis, say so in the
     slide's speaker notes rather than dropping it silently, and never add a commitment
     the manager did not record. If the list is empty, skip this section.
  2. **CRM action plan: execution status**: from `team_action_plan`, completion rate
     ("Last period: 7 of 9 CRM actions completed (78%)") and any missed or flagged
     items. Frame this as deal-execution accountability, not coaching. **Do not conflate
     it with the coaching commitments above: they are two distinct streams.**
  3. **Documented coaching history**: non-fixture `coaching_history` events in date
     order, each with its lifecycle state (planned, scheduled, completed, acknowledged,
     later assessed). State whether comparable later-period evidence exists. A completed
     receipt proves documented support, not that the pattern persisted or that coaching
     produced an outcome; an outcome may be described as recorded after coaching, never
     as caused by it. If admissible history is absent, say so rather than substituting
     intervention-ledger rows.
  4. **3–5 numbered recommendations**, each with a bold headline (what to do) and one
     supporting sentence (why, with evidence). Where documented history shows an earlier
     attempt at the same gap without later movement, propose a different approach. Use
     emerald numbered circles as markers and give each recommendation room.
- This is the most important slide in the 1:1: continuity on what was agreed, deal
  execution, whether past coaching on this gap stuck, then forward actions.
- No employment recommendation, rating, leaderboard or named-rep comparison.

#### Slide 8b: Renewal and expansion signals (optional)

- Render only if the org tracks renewals and post-sale value.
- **Data:** `list_account_contracts` for the rep's top accounts, `list_impact_entries`
  per contract.
- **Layout:** 2–3 stat cards (renewals in the next 90 days, at-risk contracts, expansion
  opportunities identified), then a table of account, contract status, renewal date,
  post-sale impact and expansion signals, with 1–2 specific value achievements or
  expansion hooks per contract. Status dots: red for at-risk, emerald for healthy or
  expansion-ready.

#### Slide 9: Focus areas for next week

- **Background:** Off-white.
- **Data:** synthesised from all evidence.
- **Layout:** 3–5 specific, time-bound actions, each naming a deal or account, in a
  checklist layout:
  - "Schedule a champion-identification call with Acme Corp (deal $450K, health 0.32)"
  - "Re-engage GhostInc: 62 days dormant, $85K ARR at stake"
  - "Update the decision-criteria evidence on the TechCo deal before Thursday"

#### Slide 10: Closing

- **Background:** Navy.
- **Content:** "Let's make this the best quarter yet.", company name, date.
- **Layout:** clean and centred, mirroring the title slide.

---

## Step 5: Generate, QA and deliver

Write one generator with the host's presentation toolchain
([host-adapters.md](host-adapters.md#building-slides)) that:

1. embeds all pulled data directly (no external data files);
2. uses the factory helpers above (when building with PptxGenJS (Claude's pptx skill),
   fresh option objects per call, because PptxGenJS mutates them);
3. builds every slide in the specification, skipping optional slides without evidence;
4. handles missing data, empty arrays, indeterminate payloads and zero values per
   [Handling missing data](#handling-missing-data);
5. saves `Rep-Coaching-Report-{RepName}-{YYYY-MM-DD}.pptx` where the host keeps
   deliverables ([host-adapters.md](host-adapters.md#saving-and-delivering-files)).

Then QA, following [host-adapters.md](host-adapters.md#rendering-and-inspecting-slides):

1. Run the host's presentation validation on the deck and fix every failure in the
   generator.
2. Render every slide with the host's render step. Inspect **each slide at full size**.
3. Fix overlap, clipping, wrapping, a number split from its unit, low contrast and
   leftover placeholder copy.
4. **Content check:** spot-check every number against the tool payload; confirm health
   colours follow `score_semantics`; confirm no organization-wide figure is labelled as
   the rep's.
5. **Sensitive-detail leakage check:** no other rep's name or data, no raw permission
   errors or stack traces, no tool prefixes, hashes or internal IDs, and no fixture
   record presented as real.
6. Re-render only the slides you changed, then stop.

Return **one clickable link** to the final PPTX plus a short note on material evidence
gaps (unavailable lenses, fallbacks used, indeterminate payloads, fixture exclusions).

---

## Step 6: Post-session capture

**This step runs after the 1:1**, typically hours or days after the report, often in a
separate conversation. It turns the one-shot report into a persistent coaching thread:
action items captured here flow into the next session's `previous_action_items`.

It is **optional** and **never** a side effect of report generation.

### Capability check first

The writes are `complete_coaching_session` (attest and complete a session) and
`record_coaching_outcome` (a later outcome assessment). As at 2026-10-13 **neither is
exposed** by the connected Summit53 connector; `list_available_tools` lists only
read-only coaching tools.

Before anything else, check the live tool list and schema:

- **Not exposed → do not attempt it.** Run the gathering conversation below, produce a
  structured draft (session, date, notes, agreed action items with owner and due date),
  state clearly that **nothing was saved**, and tell the user to record the session in
  the product's `/coaching` page, where the action items will then carry forward.
- **Exposed →** continue with the workflow below, under its approval rules.

### Trigger phrases

"log my notes from the session with [Rep]", "close out the [Rep] 1:1", "record the action
items from my coaching session with [Rep]", "complete coaching session for [Rep]", "save
my 1:1 notes", "log action items for [Rep]", and, for outcomes only, "record how the
coaching on [metric] turned out for [Rep]".

### Workflow

Both writes are approval-gated. Never call either without an explicit user request for
that specific write, the connector's approval flow, and an idempotency key where the
schema supports one. Completing a session records what occurred; a later outcome is a
separate audit event that needs its own request.

1. **Retrieve and verify the session.** Use the `session_id` captured from
   `coaching_agenda` during report generation, or re-pull `coaching_agenda(rep_id)`; it
   returns the current-week session, usually still `status: scheduled` if the session is
   being closed promptly. Verify the organization, rep and status. If the session is
   already `completed`, stop and tell the manager. Do not overwrite; ask whether they
   meant a different session.
2. **Gather notes and action items conversationally.** Don't demand structured input:
   - "What came out of the session? Any key takeaways or observations?"
   - "What did you and [Rep] agree as action items?"
   - If notes are vague, reflect and sharpen: "Improve discovery" → "Record and review
     one discovery call before Thursday's sync". Let the manager approve or edit.
3. **Inspect the live schema and current session state.** If the user asked to complete
   the session, call `complete_coaching_session` **once** with the manager attestation,
   occurred and completed timestamps, notes, action items, evidence or provenance,
   idempotency key and approval receipt the schema supports. Never guess a receipt or
   re-complete a session.
4. **Confirm back** in conversational prose, from the confirmed saved result only: how
   many action items were recorded, and that they will appear as
   `previous_action_items` in the next session's agenda. Don't read the items back
   verbatim unless asked; the manager just dictated them.
5. **Record a later outcome only on a separate explicit request.** Completing a session
   is not permission to record an outcome. Verify the session is completed, then call
   `record_coaching_outcome` with the baseline window, later window, assessment date,
   evidence, outcome status, notes and follow-up date the schema supports, plus
   idempotency and approval. Never infer an outcome from pipeline movement or fill
   missing evidence. Use correlational language ("changed after", "was associated
   with"), never "caused by". An outcome assessment is not an employment finding.

Completion documents what support was delivered. It does not record acknowledgement,
prove persistence or establish an outcome.

### Good action items

Steer the manager toward items that are:

- **Specific:** "Pair-qualify 5 new ICP accounts before next 1:1", not "improve
  qualification".
- **Time-bound:** a check-in point or deadline where realistic.
- **Evidence-generating:** something observable by the next session (a completed task,
  a metric shift, a recorded call, a document).
- **Owned:** clear whether the rep or the manager drives it.

If items miss these, offer one or two sharpened versions and let the manager approve or
edit. Don't lecture; respect their judgement.

### Edge cases

- **No session found.** If `coaching_agenda` returns "No active coaching cadence found",
  tell the manager there is no scheduled session to close, offer the structured draft,
  and direct them to the `/coaching` page to set up a cadence.
- **Session already completed.** Stop and surface it rather than overwriting.
  Re-completion behaviour isn't guaranteed, and a silent overwrite would lose coaching
  continuity.
- **Partial information.** If the manager has notes without action items (or the
  reverse), pass only what was provided where the schema allows empty fields.
- **No explicit approval, or the write is not exposed.** Produce the structured draft
  and state that nothing was saved.

### What this unlocks

Once a session is completed (here or in the `/coaching` page), the next report for this
rep finds those items in `coaching_agenda.previous_action_items`, and they open Slide 8
as the accountability header. That is the continuity loop: report → 1:1 → close → next
report carries the commitments forward. Managers and reps arrive at every 1:1 already
knowing what was agreed last time.

---

## Tips for great coaching reports

- **Be specific, not generic.** "Improve discovery" is useless. "Ask Acme Corp's VP of
  Engineering who approves the budget" is coaching.
- **Balance positive and constructive.** Start with what's going well before the gaps.
- **Ground recommendations in data.** Every suggestion traces to a specific metric,
  score or pattern.
- **Make it conversational.** The deck should spark discussion, not deliver a verdict.
  Frame gaps as upside: "Here's where the biggest opportunity is hiding."
- **Keep it short.** About 10 slides. The 1:1 is a conversation, not a presentation
  marathon.

---

## Tools

Logical names; resolve the connector prefix at runtime per
[connector-preflight.md](connector-preflight.md) and load them in one batch per
[host-adapters.md](host-adapters.md#loading-the-summit53-tools).

| Tool | Role | Required? |
|---|---|---|
| `current_context` | Tenant and membership gate (first call) | Required |
| `list_available_tools` | Confirm which coaching capabilities, including writes, are exposed | Required |
| `coaching_intervention_plan` | Roster, `user_id`, flag quality | Required |
| `coaching_diagnostic` | Thesis: layer, focus metric, P75 gap, `_evidence` | Required |
| `coaching_agenda` | `session_id`, session context, `previous_action_items` | Required |
| `coaching_meeting_analytics` | Call behaviour | Required |
| `coaching_development` | Goals, diagnostic history, focus-metric trend | Required |
| `coaching_history` | Delivered-coaching record | Required |
| `rep_coaching_context` | Aggregate fallback | Fallback |
| `revenue_loop_diagnosis`, `hunter_farmer_mix`, `ramp_cohort` | Lenses (permission-gated) | Optional |
| `capacity_to_target_planner` (`group_by: "sales_region"`, `level: "leaf"`) | Rep's region group and grouping warnings | Optional |
| `segment_performance_summary` (`dimension: "sales_region"`) | Region comparator (analytics permission) | Optional |
| `get_opportunity` | `sales_team_at_close` for cited closed deals (pending deploy) | Optional |
| `list_methodology_playbooks` | Org's framework definitions | Required |
| `forecast_confidence`, `risk_heatmap`, `pipeline_risk_summary` | Pipeline, deal health, distribution | Required |
| `activity_gaps`, `get_opportunity_activities` | Engagement and cadence | Required |
| `opportunity_framework_summary` | MEDDPICC per deal | Required |
| `get_opportunity_notes_summary`, `get_opportunity_notes`, `get_opportunity_signals` | Narratives, blockers, first-constraint | Required |
| `deal_drag_dashboard`, `deal_drag_summary` | Drag (dashboard rep-scoped; summary organization-wide) | Required |
| `team_action_plan` | CRM action execution | Required |
| `outreach_funnel_summary`, `search_outreach_leads` | Outreach health | Optional |
| `list_account_contracts`, `list_impact_entries` | Renewal and expansion | Optional |
| `list_interventions`, `get_intervention_outcome` | Deal-execution accountability only | Optional |
| `complete_coaching_session`, `record_coaching_outcome` | Approval-gated writes; **not exposed as at 2026-10-13** | Step 6 only |

**Never used to scope a rep:** `search_opportunities`, `search_accounts` (no owner
filter).
