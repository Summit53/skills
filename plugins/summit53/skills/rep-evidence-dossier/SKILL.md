---
name: "rep-evidence-dossier"
description: "Assemble a neutral, defensible Summit53 evidence dossier as a PPTX for a promotion case, PIP, talent calibration, documented performance concern or HR meeting. Screens structural confounders and documentary depth before any performance evidence, closes with an evidence register, and never renders an employment recommendation. Use when a manager says 'build the promotion case for [rep]', 'prep me for calibration', 'we're considering a PIP for [rep]', 'HR wants documentation on [rep]', 'pull together the performance record for [rep]', 'why them and not [other rep]?' or 'what have we done to help this rep?'. Do not use for routine coaching or 1:1 prep — use rep-coaching-report."
version: "3.1.0"
baselined: "2026-10-13"
status: "active"
---

# Rep Evidence Dossier

Assemble the documentary record for a human employment decision: promotion, PIP,
calibration or documented performance concern. The dossier is a PPTX that puts
documentary depth and structural confounders ahead of any performance evidence, and it
**renders no recommendation**.

## Route first

- Routine developmental coaching, recurring 1:1 prep, "what should I coach them on?" →
  `rep-coaching-report`. Do not build this dossier for a normal 1:1.
- Promotion, PIP, calibration, talent review, HR documentation or a formal performance
  decision → this skill.
- Logging a coaching session, notes, actions or outcomes → not this skill. This skill
  never writes (see [Guardrails](#guardrails)).

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete
its checklist before any data call. Then apply these dossier-specific gates:

1. **Demo label.** This is an employment artifact. When the tenant is Staging or a demo
   tenant, or provenance cannot cleanly separate fixtures from real records, every slide
   carries **Demo data — not for employment decisions**. Every Staging forward test
   carries it on every slide, even when fixture rows were excluded.
2. **Load tools in one batch.** Use one ToolSearch `select:` call for every tool in the
   [tools table](#tools), resolved to the connector that passed `current_context`.
3. **Inspect the live schema of every tool before calling it.** As at 2026-10-13 the
   live connector has these shapes, and the workflow below is written against them. If
   the live schema differs, follow it and note the difference in the evidence register:
   - `search_opportunities` has **no owner or rep filter**. It cannot scope a book to a
     rep, so this skill does not use it for rep evidence.
   - `hunter_farmer_mix` (`window_quarters` only) and `ramp_cohort` (no arguments) are
     roster-level. Call them unfiltered and select the row whose `user_id` equals the
     rep's ID.
   - `coaching_diagnostic`, `coaching_history`, `coaching_development`,
     `coaching_agenda`, `coaching_meeting_analytics` and `rep_coaching_context` take a
     **scalar** `rep_id`. (`coaching_diagnostic` also has a batch `rep_ids`, which this
     skill does not need.)
   - `deal_drag_summary` takes no arguments and is **organization-wide**. Never present
     it as the rep's figures.
   - Rep-filterable sources: `risk_heatmap(reps: [id])`, `forecast_confidence(reps:
     [id])`, `pipeline_risk_summary(reps: [id])`, `deal_drag_dashboard(reps: [id])`,
     `activity_gaps(owner_ids: [id])`, `team_action_plan(user_id: id)`.
4. **Resolve the rep from the roster.** Take the rep's `user_id` from
   `coaching_intervention_plan`, never from opportunity ownership or a name search.
5. **Viewer authorization.** The requester must be authorized for this rep's coaching
   record (manager scope). A permission refusal on a coaching tool is a finding, not a
   reason to substitute other data.

## References

Read all four before the first data call:

- [references/connector-preflight.md](references/connector-preflight.md): the tenant,
  schema, fixture, read-only, missing-evidence, correlation and delivery contract.
- [references/structural-confounders.md](references/structural-confounders.md): **the
  six screens and the two-tier depth gate. Run these first.** Its output contract fixes
  the order of the deck.
- [references/delta-attribution.md](references/delta-attribution.md): for any rep
  metric presented as a movement or trajectory.
- [references/async-envelopes.md](references/async-envelopes.md): a processing envelope
  read as data produces a blank section, which in this artifact means missing evidence
  in an HR meeting.

---

## The moments this serves

Serves **RL7 — defending a promotion** and **RL8 — putting someone on a PIP**.

**RL7 — calibration.** Manager to VP/CRO, with peer managers in the room. The dreaded
question comes from a peer whose candidate just got passed over: *"Why them and not
[other rep]?"* Today the case is assembled from memory and last quarter's numbers, in a
room where everyone is doing the same and the loudest advocate wins.

**RL8 — the PIP.** Manager, HR, sometimes legal. The dreaded question is not about the
rep: *"What did you do to help them before this?"* A thin answer makes the PIP
indefensible and ends the **manager's** career, not the rep's. Today that means
reconstructing months of coaching history from calendar invites and memory.

## The constraint that governs everything

**This artifact carries employment-law exposure.** In New Zealand and Australia a
personal grievance claim will test exactly this documentation: whether the decision was
one a fair and reasonable employer could reach, and whether a fair process preceded it.

Four rules follow, and none are negotiable:

1. **The dossier renders no recommendation.** It does not conclude the rep should be
   promoted, managed out or retained. It assembles evidence and hands the decision to
   the human accountable for it. A tool that recommends a PIP has, in a hearing, made
   the decision, and the manager cannot then claim to have exercised judgement.
2. **Structural confounders appear before performance evidence.** This is document
   order, not tone. See
   [references/structural-confounders.md](references/structural-confounders.md).
3. **Absence is reported, never omitted.** A missing record is a finding. An empty
   section is a defect.
4. **The record is read, never written.** Never complete, create, edit or backfill a
   coaching session, goal, agenda, meeting record, intervention, note or outcome. A
   record created to feed this dossier is exactly what a grievance process is designed to
   detect.

Getting this right is a credibility asset, not just risk management. It is also the
honest position: the platform can assemble evidence far better than it can adjudicate a
person's career.

## What changed in 3.0.0

- **PPTX is the primary artifact**, with a visible evidence-register appendix and a
  3–4 slide stop-gate deck. Findings are written as sourced sentences (see
  [Slide rules](#slide-rules)).
- **`coaching_history` is the primary depth source**; the other coaching reads
  corroborate it or serve as labelled fallbacks.
- **Two-tier depth gate**: provisional versus full stop, matching
  [references/structural-confounders.md](references/structural-confounders.md).
- **Bug fix:** earlier versions rep-filtered `search_opportunities`, which has no owner
  filter. Book composition and segment membership now come from rep-filterable sources
  (`risk_heatmap`, `forecast_confidence`).
- **Fixture exclusion** and the employment demo label are mandatory.

Carried forward from 2.x:

- **`complete_coaching_session` is not used.** It was never exposed to this skill. The
  close-the-loop half of the original `rep-coaching-report` had no backing tool and
  would have failed at the moment a manager tried to log a session. This dossier writes
  nothing.
- **`coaching_diagnostic` and `coaching_agenda` are read-stored**, not get-or-generate.
  Where nothing was stored they return an empty, "not found" or `not_generated`
  response, not an error. This skill treats that as a record-state finding.

---

## Step 1 — Establish purpose and rep

Ask which rep, and **ask what decision this supports**: promotion, PIP, calibration or
general documentation. The purpose changes what the dossier emphasises, and asking it on
the record is itself good process.

If the user declines to name a purpose, default to **calibration**, the least
prejudicial framing, and disclose the default on the mandate slide.

Record the purpose, requester, organization name, subject and as-of timestamp for the
mandate slide.

## Step 2 — Run the confounder screens first

Do not pull performance data yet. Run the six screens in
[references/structural-confounders.md](references/structural-confounders.md), in this
order:

| Screen | Tool(s) |
|---|---|
| 1. Flag base rate and persistence | `coaching_intervention_plan` (`coaching_flag_quality`, `ordering`, per-rep `evidence_sufficiency`) |
| 1b. Benchmark meaning and verified values | `coaching_diagnostic(rep_id)` → `benchmark_context`, `results_scores._evidence` |
| 2. Territory, segment and sales region | `segment_performance_summary`, plus the rep's book from `risk_heatmap(reps: [id], period_span: 2)` or `forecast_confidence(reps: [id])`; region group and warnings from `capacity_to_target_planner(group_by: "sales_region", level: "leaf")`; `sales_team_at_close` from `get_opportunity` for closed deals, where exposed |
| 3. Ramp status and survivorship | `ramp_cohort` (roster-level; select `user_id`) |
| 4. Role–motion fit | `hunter_farmer_mix` (roster-level; select `user_id`) |
| 5. Evidentiary depth | `coaching_history(rep_id)` **primary**; `coaching_development`, `coaching_meeting_analytics`, `coaching_agenda`, `rep_coaching_context` corroborate or fall back |
| 6. Ledger scope | `list_interventions`, `get_intervention_outcome` (owner-filtered locally) |

Screen notes:

- **Screen 2.** Segment membership must come from a rep-filterable source. If the rep's
  rows carry no segment or territory field, record that segment membership could not be
  resolved and do not fall back to the blended average as if it were like-for-like. On
  `risk_heatmap`, check `scope_summary.truncated_by_period`; if `true`, widen
  `period_span` and re-pull before counting anything.
- **Screen 2 — sales region (optional enhancement).** Call
  `capacity_to_target_planner(group_by: "sales_region", level: "leaf")` at roster level
  and locate the planning group containing the rep. Record the rep's leaf region as a
  structural factor and compare within that region (or segment) before any team-wide
  figure. Quote the grouping warnings verbatim in the evidence register:
  `reps_without_team` (if it names this rep, region comparison could not be made — say
  so on slide 3), `market_quota_unassigned`, `region_grouping`,
  `owner_profile_attribution`. If the response is `insufficient_data`, falls back to a
  single blended group, or the rep is in no group, record region membership as **not
  resolved**; never infer it. Never attribute a region's quota, capacity or gap to the rep,
  and never list other reps from the group's contributors.
- **Screen 2 — team at close (pending deploy; optional).** Where the live `get_opportunity`
  schema exposes `sales_team_at_close{id, name, team_type, source}` (null while open), read
  it for each closed deal cited in the dossier and attribute the deal to the team the rep
  was in at close, not their current team. For a rep who moved teams, closed-deal evidence
  is compared against the region of the team at close, and slide 3 says the rep's history
  spans more than one team. If the field is not exposed, record in the evidence register
  that closed deals were attributed to the rep's current team assignment and add it to the
  standing limits when the rep is known to have moved.
- **Screens 3 and 4.** If the rep is absent from `ramp_cohort.reps[]`, ramp status is
  "not in a current ramp window", not "fully ramped". An empty payload with
  `requires_manager_role` means ramp status could not be established. A
  `hunter_farmer_mix` classification of `unknown` means role-fit could not be assessed;
  never read it as "no mismatch". Shares can arrive as numbers or decimal strings
  (including `"0E+2"`), so cast before comparing.
- **Screen 5.** Prefer `coaching_history` for dated sessions, completion events,
  provenance, manager notes, action items and linked meeting evidence. Keep plan,
  scheduled, completed, acknowledged and later-assessed states distinct. Assigned
  interventions that `coaching_history` returns separately are not coaching delivered.
  `rep_coaching_context` bundles the coaching reads in one call. Use it when a granular
  call is refused, and label the fallback. If the bundle and a granular call disagree,
  use the granular value and note the discrepancy. A coaching capability that is not
  exposed is **unavailable**, never zero.
- **Fixture filter.** Before computing any count, exclude rows marked `synthetic`,
  `demo_seed`, `demo_fixture`, seeded, generator or `[DEMO]`/`demo-` per
  [references/connector-preflight.md](references/connector-preflight.md). If no real
  rows remain, the admissible count is zero, even when the raw Staging response is not.

### The depth gate (two tiers)

Compute and render the depth table from
[references/structural-confounders.md](references/structural-confounders.md) Screen 5
before any performance content: weeks of stored diagnostic history, development goals,
completed coaching sessions with provenance, sessions with manager notes or action
evidence, meetings analysed and linked meeting evidence, stored agendas available, and
interventions assigned to the rep (labelled as execution accountability).

**Tier 1 — provisional.** If any of these holds: fewer than 6 weeks of diagnostic
history, zero development goals, zero completed coaching sessions, or zero meetings
analysed. Then open with the insufficient-evidence banner from the reference, and put
**Provisional — insufficient documentary depth** visibly on every later slide that
presents or interprets evidence.

**Tier 2 — full stop.** If all of these are zero: diagnostic history, goals, completed
sessions and meeting evidence. Then **stop before performance evidence** and build only
the stop-gate deck (Step 4). The record-state finding:

> No documented coaching record exists for this rep in Summit53: 0 weeks of stored
> diagnostic history, 0 development goals, 0 completed coaching sessions, 0 meetings
> analysed. This dossier cannot support a performance decision. It can only report that
> the documentary record required to defend one has not been created.
>
> Coaching delivered outside the platform will not appear here. If it occurred, it needs
> to be documented before this decision proceeds.

That is a complete and useful deliverable. A manager who learns this before the HR
meeting can still act on it. Padding it out with pipeline numbers to make it look
substantial would actively mislead, because it would suggest evidence exists where it
does not.

Live check on Staging: one rep returned 1 week of history, 0 goals and 0 meetings;
another rep's agenda returned `status: "not_generated"`; a third returned "Rep
diagnostic not found or unavailable". **This gate will trip on real data.** It is not a
defensive edge case.

## Step 3 — Performance evidence (only if the gate permits)

Every item below is a **finding**, never a verdict. Each carries a comparator, a window
and an evidence status.

**Attainment and pipeline**
- `forecast_confidence(reps: [id])`, and unfiltered for the team comparator. State that
  a team comparator spans segments and is therefore not like-for-like.
- `pipeline_risk_summary(reps: [id], period_span: 2)`. Use only rep-scoped fields
  (`byRep`, `repMetrics`, `totalDeals`, `byRiskLevel`, `velocityMetrics.stuckDeals`).
  Never attribute `quota`, `coverageRatio`, `totalForecast` or `gap` to the rep unless
  the response's scope metadata confirms they are rep-filtered.
- Book composition from `risk_heatmap(reps: [id], period_span: 2)`, re-pulled wider if
  `truncated_by_period` is `true`. `healthScore` is 0–1 and higher is healthier; read
  `score_semantics` rather than inferring polarity from a field name.

Compare against the **rep's segment**, per Screen 2.

**Execution behaviour**
- `activity_gaps(days: 30, owner_ids: [id])`. An empty list with scope metadata means no
  gaps were found. A bare `{}` or a payload without scope metadata is **indeterminate**,
  so do not report it as engagement.
- `deal_drag_dashboard(reps: [id])` for the rep's stalled deals. Where drag-cause or
  recovery analytics carry an unavailable marker, report them unavailable.
  `deal_drag_summary` is organization-wide: use it only as a labelled team comparator.
- `team_action_plan(user_id: id)` for action completion, labelled as deal-execution
  follow-through.

**Qualification discipline**
- `opportunity_framework_summary` on up to 8 of the rep's deals from `risk_heatmap`.
  Report completion and component scores together; completion is not competence.
- `list_methodology_playbooks`: the org's own definition of "what good looks like".
  Grounding the standard in the org's published playbook rather than a generic one
  matters here. A rep cannot be held to a standard that was never published to them, and
  that argument lands hard in a grievance process.

**Observed meeting behaviour**
- `coaching_meeting_analytics(rep_id, weeks: 13)`: talk ratio, question rate,
  monologue length, interruptions.

This is the most defensible category in the dossier because it is **observed behaviour
rather than opinion**. Where `total_meetings` is 0, say so: the category is
unavailable, not neutral.

**Development trajectory**
- `coaching_history`: the dated session timeline, with lifecycle state per event.
- `coaching_development`: 13-week diagnostic history, 26-week focus-metric trend,
  development goals with progress.

Where history exists, this is the evidence trail. Render it as a dated timeline. Where
`focus_metric_trend` is populated, present it per
[references/delta-attribution.md](references/delta-attribution.md): movement with a
stated comparison window, not a bare current value.

**Diagnostic values.** Cite a `results_scores` value only if
`_evidence[metric].verified` is `true`. Otherwise report the metric as **not
established** and name the status (for example `legacy_unverified`). A benchmark without
a verified rep measurement is not a gap. Team P75 benchmarks are **aspirational targets,
not peer averages**: quote the returned `benchmark_context.warning` verbatim, state
`peer_count`, and render every gap as a magnitude. Where the gap is under 10%, say it
does not support a performance conclusion. An empty `low_scoring_components` is a
positive finding and belongs in the dossier.

## Step 4 — Build the PPTX

Save `Rep-Evidence-Dossier-{RepName}-{YYYY-MM-DD}.pptx` to the session's outputs
directory. Build it with PptxGenJS following the `pptx` skill: read that skill's
SKILL.md (and its PptxGenJS reference where present) before writing code, and build a
structured 16:9 deck with a theme, layouts and sections. A DOCX companion is produced
only on explicit request, after the PPTX, from the same reconciled evidence, using the
`docx` skill. Do not create a standalone Markdown dossier by default.

### Deck structure follows the gate

- **Full stop (Tier 2).** Build only a three- or four-slide record-readiness deck:
  1. Mandate and purpose, with the no-recommendation statement.
  2. Evidentiary depth and the stop finding (the record-state finding above).
  3. Structural screens and unavailable evidence.
  4. *(Optional)* Limits, what evidence must accrue through the ordinary coaching
     process, and the evidence register.

  Include no performance, behaviour, attainment, pipeline, execution, qualification,
  trajectory, ranking or implied-verdict content, in visible text or in speaker notes.
- **Provisional (Tier 1).** Use the full-pack sequence. Put **Provisional — insufficient
  documentary depth** on every slide after the gate that presents or interprets
  evidence, styled distinctly from the ordinary footer.
- **Admissible full pack.** Use the sequence below. Omit a slide when its evidence is
  unavailable rather than padding it, but always keep the mandate, gate, limits and
  evidence-register slides.
- **Demo forward test.** On an explicitly read-only Staging demonstration, compute and
  show the formal-use gate from admissible records first. A full visual demonstration
  may then use the excluded fixture data only if **Demo data — not for employment
  decisions** is visible on every slide, and the gate slide states whether formal use
  would have stopped. Never use this exception in a real employment workflow, and never
  describe fixture evidence as admissible.

### Full-pack sequence

1. **Mandate and purpose**: subject, purpose (and whether it was defaulted), requester,
   organization name, as-of time, and a prominent statement: *"This dossier renders no
   recommendation. It assembles the documentary record and the structural factors
   bearing on it. The decision, and the reasoning for it, belong to the manager."*
2. **Evidentiary depth and gate**: the depth table, provenance, availability, and the
   resulting full, provisional or stop state. Always slide 2.
3. **Structural factors**: territory and segment, ramp and survivor bias, role–motion
   fit. Mark each found, not found, or not assessed with a reason, and state what it
   means for the weight the later evidence can carry.
4. **Signal reliability and comparator quality**: flag base rate and persistence,
   benchmark role and `peer_count`, like-for-like status, intervention-ledger scope.
5. **Dated coaching record**: the `coaching_history` timeline with lifecycle states,
   goals and progress, manager notes and action items, and assigned interventions
   labelled as execution accountability, not coaching delivered. Where the record is
   thin, say how thin.
6. **Observed behaviour**: recorded-meeting evidence, or explicit unavailability.
7. **Attainment and pipeline**: dated measurements against the rep's segment, with the
   comparator and window named.
8. **Execution and qualification**: activity, deal drag, framework evidence, and the
   org's published methodology standard.
9. **Trajectory**: only when the delta-attribution gates pass. Otherwise state the
   limitation on the most relevant earlier slide instead of drawing a movement chart.
10. **What this dossier cannot establish**: the standing limits below plus run-specific
    gaps, including the deliberate absence of a recommendation.
11. **Evidence register** (appendix): one row per material claim or metric, with
    logical capability, as-of or retrieval date, window, comparator, evidence status
    (verified, unverified, unavailable, not generated, excluded as fixture), warnings
    quoted, and async or fixture screening notes. It is audience-visible provenance;
    speaker notes do not replace it. Continue it across slides rather than shrinking
    the text.

### Standing limits (slide 10)

Include every one that applies. These are not hedges; they are the boundary of what the
record supports, and a decision-maker needs them.

- **Coaching outside the platform is invisible.** The record reflects what was stored in
  Summit53, not what occurred.
- **Ramp benchmarks are survivorship-biased.** They cover only reps currently in their
  ramp window and exclude everyone who left. Read them as a best case. Attrition is not
  tracked.
- **The Intervention Ledger is not rep-scoped.** Its entity types are account,
  opportunity, source and lead. Records shown are interventions *assigned to* this rep,
  not coaching *delivered to* them.
- **Intervention and coaching outcomes are correlational.** The ledger reports
  `causal_claim_supported: false`. Movement within an outcome window is association.
- **Segment comparisons rest on territory resolution**, not an explicit segment field.
- **Region comparisons rest on current Sales Org team membership** unless
  `sales_team_at_close` was available; reps without a team, or market quota left
  unassigned, weaken them (quote the warnings).
- **Attainment is not adjusted for account quality or inherited pipeline.** No tool
  measures the book a rep was given versus the book they built.
- **Meeting analytics cover recorded meetings only.** Unrecorded coaching does not
  appear.
- **Fixture and demo records were excluded** (state the count where known).
- **No recommendation is rendered, by design.**

### Slide rules

The 2.x skill refused PPTX because slides invite summary bullets, and a summary bullet
in a grievance file is a liability. That risk is real, so the deck is built to avoid it:

- **Findings are complete, sourced sentences**: a measurement, its comparator, its
  window and its source. Never a verdict bullet, a fragment ("Discovery: weak") or a
  summary judgment. Measurement tables are fine; judgment columns are not.
- **Slide titles name the topic neutrally** ("Attainment against the Enterprise segment
  benchmark"), never a conclusion ("Attainment is behind").
- **No traffic-light rep ratings, talent quadrants, ordinal rankings, star ratings,
  scorecards or red/green visual judgments about the person.** Colour encodes data
  categories or emphasis, never a rating of the rep.
- **Design**: a neutral evidence-publication style. Dark title and limits slides, light
  editorial evidence slides, slate and blue as the core palette, restrained orange and
  teal accents. Prefer dated timelines, restrained native charts and editorial tables to
  dashboard card grids. No stock photography or decorative headshots.
- **Type**: deck title at least 50 pt, slide titles at least 35 pt, subheads at least
  24 pt, body at least 16 pt. Use Cambria headings and Calibri body, which render
  true-to-width in QA. Shorten content or continue onto an appendix slide rather than
  shrinking text or allowing clipping.
- **Proportionate detail.** Keep sensitive detail proportionate to the formal purpose.
  Never expose another rep's evidence outside the calibration rule in Step 5; aggregate
  comparators otherwise.
- **Interpretation-changing limits stay on the slide**, not only in the notes.
- **Speaker notes** carry a `[Sources]` block on every evidence-bearing slide: logical
  capability, retrieval or as-of date, window, comparator, evidence status and any
  warnings needed to interpret the slide.

## Step 5 — Language rules

Enforced by review before delivery. Search all visible text **and speaker notes** for
each.

**Banned, because these are conclusions the dossier is not entitled to draw:**
`underperformer`, `poor performer`, `not meeting the bar`, `failing`, `should be`,
`recommend`, `needs a PIP`, `unable to`, `lacks`, `caused`, `because of their`,
`due to poor`.

**Required substitutions:**

| Instead of | Write |
|---|---|
| "Rep is underperforming" | "Attainment is X% against a segment benchmark of Y% for {window}" |
| "Coaching didn't work" | "Focus metric moved from X to Y over the window; the record does not establish why" |
| "Rep lacks discovery skills" | "Discovery score averaged X across N deals, against the org playbook standard of Y" |
| "Below benchmark" | "X against a team-P75 benchmark of Y (n=N), a gap of Z%. Below team P75 does not by itself mean below-average performance." |
| "Needs a PIP" | *(nothing: the dossier does not say this)* |
| "Intervention worked" | "Metric moved X → Y in the outcome window; ledger label 'worked'; correlational" |

Every performance statement is a **measurement with a comparator and a window**. If a
sentence cannot be written that way, the underlying data does not support the sentence.

**Peer naming (calibration only).** Naming a comparison rep is permitted **only** in
calibration mode, only using the same metrics on the same window and same segment, only
with the segment caveat attached, and only when the requester is authorized for that
rep's data. Otherwise use aggregate comparators. Cross-segment rep comparison is not
evidence and must not appear. Never render an ordinal rank.

## Step 6 — Verify

A dossier that generates cleanly and says nothing has failed, and in this artifact a
thin section is worse than no section.

1. **Format.** The primary artifact is a `.pptx` named to the contract; no standalone
   Markdown was produced by default.
2. **Order.** Evidentiary depth is slide 2 and structural factors precede all
   performance content. If not, the dossier fails its core constraint.
3. **Depth gate.** If the full stop fired in a formal run, the deck has only three or
   four slides with no performance, behaviour, attainment, pipeline, execution,
   qualification or trajectory content in visible text or notes. If the provisional gate
   fired, the label is on every applicable downstream slide.
4. **No recommendation.** Search visible text and notes for the banned list. Zero hits.
5. **Comparators.** Every performance value has a named comparator, window, evidence
   status, source date and source, and the evidence register reconciles them. Region or
   segment comparators precede team-wide ones; region-grouping warnings are quoted.
6. **Verified values only.** No `results_scores` value is cited where
   `_evidence[metric].verified` is not `true`; every P75 comparison carries the
   aspirational-benchmark warning and `peer_count`.
7. **Absences rendered.** Every unavailable source is stated as unavailable. Cross-check
   the tool list against the slides. No `null`, `[]`, `{}`, `not_generated` or "not
   found" is rendered as `0`. Live traps: `total_meetings: 0`, `development_goals: []`,
   `coaching_agenda.status: "not_generated"`.
8. **Causal language.** Search for "caused", "because", "led to", "resulted in",
   "proves", "shows that they". Rewrite each.
9. **Ramp caveat.** Every ramp figure has the survivor-cohort caveat on the same slide,
   not in a footnote; an n=1 cohort shows no median.
10. **Ledger labelling.** Intervention records are labelled assigned-to, never
    coaching-delivered.
11. **Scope.** No organization-wide figure (`deal_drag_summary`, unscoped `quota` or
    `coverageRatio`) is attributed to the rep; nothing claims `search_opportunities` was
    rep-filtered.
12. **Fixtures and writes.** No fixture record is presented as admissible; the demo
    label is on every slide where required; no write capability was called.
13. **Visual QA.** Render every slide to an image (the `pptx` skill's soffice → pdftoppm
    flow) and inspect each at full size. Fix overlap, clipping, wrapping, unresolved
    placeholders, unreadable labels, exposed sensitive detail and source mismatches. Run
    the `pptx` skill's `validate.py` and require no errors. Body text is at least 16 pt,
    and `[Sources]` notes are present on every evidence-bearing slide.

Fail any of 2, 3 or 4 and the dossier must not be delivered.

## Step 7 — Deliver

Return one clickable link to the PPTX. In chat, say plainly what the dossier does and
does not do: it renders no recommendation, and the depth finding (if it tripped) is the
most important thing in it. Add a short note on material evidence gaps and anything
excluded as fixture data.

If the depth gate tripped, add one sentence on what would close the gap: which records
need to be created through the ordinary coaching process in the product's Coaching
dashboard, and that they need to accrue over time rather than be backfilled. Backfilling
a coaching record ahead of a PIP is precisely what a grievance process is designed to
detect, and it should not be suggested.

## Guardrails

- Read-only. This skill supports no write: never complete, create, edit or backfill a
  coaching session, goal, agenda, meeting record, intervention, note or outcome, and
  never pass `refresh: true`.
- Route routine coaching to `rep-coaching-report`.
- Never render an employment recommendation, an ordinal rank, a traffic-light rating or
  a talent quadrant.
- Never treat a non-discriminating flag, an unverified metric, a P75 shortfall, an n=1
  ramp cohort or an `unknown` role classification as evidence against the rep.
- Never present intervention-ledger rows or plans as coaching delivered.
- Never expose raw permission errors, tool prefixes or IDs in the deck.

## Tools

Logical names; resolve the prefix at runtime per
[references/connector-preflight.md](references/connector-preflight.md).

| Tool | Role |
|---|---|
| `current_context` | Tenant and membership gate (first call) |
| `list_available_tools` | Confirm which coaching capabilities are exposed |
| `coaching_intervention_plan` | Roster and rep IDs, flag quality, persistence (Screen 1) |
| `segment_performance_summary` | Territory comparator (Screen 2) |
| `capacity_to_target_planner` (`group_by: "sales_region"`, `level: "leaf"`) | Rep's region group and grouping warnings (Screen 2; optional) |
| `get_opportunity` | `sales_team_at_close` for cited closed deals (Screen 2; pending deploy, optional) |
| `risk_heatmap` (`reps: [id]`, `period_span: 2`) | Rep's book and segment membership; deal health |
| `ramp_cohort` (roster-level) | Ramp status and survivorship disclosure (Screen 3) |
| `hunter_farmer_mix` (roster-level) | Role–motion fit (Screen 4) |
| `coaching_history` (`rep_id`) | **Primary** dated coaching-evidence timeline (Screen 5) |
| `rep_coaching_context` (`rep_id`) | Bundled depth fallback |
| `coaching_development` (`rep_id`) | Diagnostic history, trend, goals |
| `coaching_meeting_analytics` (`rep_id`, `weeks: 13`) | Observed behaviour |
| `coaching_diagnostic` (`rep_id`) | Stored diagnostic, `benchmark_context`, `_evidence` (read-stored; handle empty) |
| `coaching_agenda` (`rep_id`) | Stored agenda (handle `status: "not_generated"`) |
| `list_interventions` / `get_intervention_outcome` | Assigned interventions only (Screen 6) |
| `forecast_confidence` (`reps: [id]` and unfiltered), `pipeline_risk_summary` (`reps: [id]`) | Attainment and pipeline |
| `activity_gaps` (`owner_ids: [id]`), `deal_drag_dashboard` (`reps: [id]`), `team_action_plan` (`user_id`) | Execution behaviour |
| `deal_drag_summary` | Organization-wide drag comparator only |
| `opportunity_framework_summary`, `list_methodology_playbooks` | Qualification against the org's own standard |

**Not used:** `search_opportunities` (no owner filter); `complete_coaching_session` and
`record_coaching_outcome` (writes; this skill writes nothing).
