---
name: rep-evidence-dossier
description: "Create a professional, neutral Summit53 PPTX evidence dossier for a formal sales-rep promotion, PIP, talent-calibration, or documented performance decision. Screen structural confounders, record depth, signal reliability, and comparator quality before presenting performance evidence, and render no recommendation. Use for formal HR, calibration, promotion, or performance documentation. Do not use for routine coaching or a regular 1:1; use rep-coaching-report."
---

# Rep Evidence Dossier

Assemble the documentary record for a human employment decision. Do not make the
decision. The dossier must render no recommendation about promotion, PIP, retention, or
termination.

## Route and safety

- Use the connected **Summit53** connector by the logical capability names in this file. Resolve the
  exposed tool dynamically; never hard-code an MCP prefix, generated hash, or namespace.
- Route routine coaching and normal 1:1 preparation to `$rep-coaching-report`.
- Keep this workflow read-only. Never complete, create, edit, or backfill a coaching
  session, goal, agenda, meeting record, intervention, note, or outcome.
- This artifact may carry employment-law exposure. Absence is a finding; never hide an
  empty source or substitute pipeline data for missing coaching documentation.
- Inspect every source's provenance, source-channel, fixture, generator, and free-text
  markers. Exclude `synthetic`, `demo_seed`, `demo_fixture`, seeded, or generated test
  rows from formal evidence and depth counts. Every Staging forward test must label the
  entire output **Demo data — not for employment decisions**, on every slide, even when
  fixture rows are excluded and never used as formal evidence.

## Read the references

Before calling Summit53, read all three:

- `references/structural-confounders.md` — the screening protocol; run it first.
- `references/delta-attribution.md` — required for any metric presented as movement.
- `references/async-envelopes.md` — processing state is not evidence.

Then load and follow the available Presentations skill completely for PPTX creation,
speaker notes, rendering, tests, visual QA, and final delivery. If the user explicitly
requests a DOCX companion, also load and follow the available Documents skill. Do not
create a DOCX or standalone Markdown artifact by default.

## 1. Establish scope, purpose, and subject

1. Call `current_context`; require a non-empty `organization.id`, an active organization
   and user, and approved membership. Stop rather than guess when tenant scope cannot be
   verified.
2. Ask which rep and whether the dossier supports promotion, PIP, calibration, or general
   documentation. If purpose is declined, use the least prejudicial framing,
   **calibration**, and disclose that default.
3. Resolve the rep ID from `coaching_intervention_plan` rather than opportunity ownership.
4. Record the request purpose, requester, organization, subject, and as-of timestamp in
   the dossier header.

## 2. Run confounder screens before performance calls

Follow `references/structural-confounders.md` in this order:

| Screen | Logical capability |
|---|---|
| Flag base rate and persistence | `coaching_intervention_plan` |
| Territory and segment | `segment_performance_summary`, `forecast_confidence` |
| Ramp and survivor bias | `ramp_cohort` |
| Role–motion fit | `hunter_farmer_mix` |
| Documentary depth | `coaching_history`, then coaching read fallbacks |
| Intervention-ledger scope | `list_interventions`, `get_intervention_outcome` |

Prefer `coaching_history` as the authoritative session/evidence timeline. Use
`rep_coaching_context`, `coaching_development`, `coaching_meeting_analytics`,
`coaching_diagnostic`, and `coaching_agenda` to corroborate it or as explicitly labelled
fallbacks when `coaching_history` is not exposed. A missing capability is **unavailable**,
not zero.

Filter synthetic and fixture-marked rows before computing every count below. If no real
rows remain, report zero admissible records even when the raw Staging response is nonzero.

### Documentary-depth gate

Render these counts before any performance evidence:

- weeks of stored diagnostic history;
- active or completed development goals;
- completed coaching sessions with completion provenance;
- sessions with manager notes and action-item evidence;
- meetings analysed and linked meeting evidence;
- stored agendas available;
- interventions assigned to the rep, separately labelled as execution accountability.

Apply both gates:

1. If there are fewer than six weeks of diagnostic history, zero goals, zero completed
   coaching sessions, or zero meetings analysed, mark every later section
   **provisional — insufficient documentary depth**.
2. If diagnostic history, goals, completed sessions, and meeting evidence are all zero,
   stop before performance evidence. Deliver only the record-state finding: the platform
   cannot support a formal performance decision from its stored coaching record.

Never suggest backfilling records ahead of a PIP. State which evidence must accrue through
the ordinary coaching process over time.

## 3. Pull performance evidence only after the gate permits

Every item is a dated finding with a comparator and window, never a verdict.

### Attainment and pipeline

- `forecast_confidence` filtered to the rep and separately to the comparison cohort.
- `pipeline_risk_summary` filtered to the rep.
- `forecast_confidence` or another authorized roster-level response for book composition;
  do not pretend `search_opportunities` is rep-filtered if its exposed schema is not.

Compare with the rep's territory-derived segment. If only a blended team comparator is
available, label it non-like-for-like. Never compare named reps across segments.

### Execution and qualification

- `activity_gaps` for 30 days and the rep owner ID.
- `deal_drag_dashboard`, `deal_drag_summary`, and `team_action_plan` filtered where the
  exposed capability supports it.
- `opportunity_framework_summary` on at most eight of the rep's deals.
- `list_methodology_playbooks` for the organization's published standard.

### Observed behaviour and trajectory

- `coaching_meeting_analytics` over 13 weeks for recorded-meeting behaviour.
- `coaching_development` for diagnostic history, focus-metric movement, and goals.
- `coaching_history` for dated sessions, completion events, provenance, manager notes,
  action items, and linked evidence.

Apply `references/delta-attribution.md` to any trajectory. When meeting count is zero,
state that observed behaviour is unavailable, not neutral.

## 4. Render the PPTX dossier

Save `Rep-Evidence-Dossier-{RepName}-{YYYY-MM-DD}.pptx` as the primary artifact. Use a
professional 16:9 presentation and return one clickable link to the final PPTX with a
short note on material evidence gaps. Do not make Markdown the primary deliverable.

### Apply the gate to the deck structure

- **Complete stop for formal use:** If diagnostic history, goals, completed sessions, and
  meeting evidence are all zero, create only a three- or four-slide record-readiness deck.
  Use: (1) mandate and purpose, (2) evidentiary depth and the stop finding, (3) structural
  screens and unavailable evidence, and optionally (4) limits, ordinary-process evidence
  accrual, and the evidence register. Do not include performance, behaviour, attainment,
  pipeline, execution, qualification, trajectory, ranking, or implied-verdict slides.
- **Partial gate:** If the documentary-depth gate is provisional, place
  **Provisional — insufficient documentary depth** visibly on every slide after the gate
  that presents or interprets evidence. Keep it distinct from ordinary footers.
- **Admissible full pack:** If the stop gate does not apply, use the evidence-led sequence
  below. Omit a slide when the evidence is unavailable rather than padding it, except for
  the mandatory mandate, gate, limits, and evidence-register slides.
- **Demo forward test:** In an explicitly read-only Staging demonstration, compute and
  display the formal-use gate from admissible records first. A full visual demonstration
  may then use excluded fixture data only if **Demo data — not for employment decisions**
  is visible on every slide and the gate slide states whether formal use would have
  stopped. Never use this exception for a real employment workflow, and never describe
  fixture evidence as admissible. The formal-use stop behavior remains unchanged.

### Use this full-pack narrative

1. **Mandate and purpose** — subject, purpose, requester, organization, as-of time, and
   the prominent statement that the dossier renders no recommendation.
2. **Evidentiary depth and gate** — required record counts, provenance, availability, and
   the resulting full, provisional, or stop state.
3. **Structural factors** — territory, segment, ramp, survivor bias, and role–motion fit;
   mark each found, not found, or not assessed with reason.
4. **Signal reliability and comparator quality** — flag base rate and persistence,
   benchmark role, sample size, like-for-like status, and intervention-ledger limits.
5. **Dated coaching record** — goals, sessions, manager notes, action items, linked
   evidence, completion provenance, and assigned interventions without describing them as
   coaching delivered.
6. **Observed behaviour** — recorded-meeting evidence or explicit unavailability.
7. **Attainment and pipeline** — dated measurements with named comparator and window.
8. **Execution and qualification** — activity, deal drag, framework evidence, and the
   published methodology standard.
9. **Trajectory** — include only when the delta-attribution gates pass; otherwise state
   the limitation on the most relevant prior slide instead of creating a movement chart.
10. **What this dossier cannot establish** — standing and run-specific limits, including
    the deliberate absence of a recommendation.
11. **Evidence register and provenance** — visible appendix mapping every material claim
    or metric to logical capability, as-of or retrieval date, window, comparator, evidence
    status, warnings, and relevant fixture/async screening.

Standing limits include coaching outside Summit53, survivor-biased ramp cohorts,
territory-derived segment comparisons, inherited-pipeline/account-quality adjustment,
recorded-meetings-only coverage, assigned-versus-delivered interventions, correlational
outcomes, unavailable sources, and the deliberate absence of a recommendation.

### Use a neutral evidence-publication design

- Use a dark title and limits/closing treatment, light editorial evidence slides, slate
  and blue as the core palette, and restrained Summit53 orange and teal accents.
- Prefer readable timelines, restrained charts, and editorial tables over dashboard card
  grids. Use no stock photography or decorative headshots.
- Do not use traffic-light rep ratings, talent quadrants, ordinal rankings, star ratings,
  or red/green visual judgments about the person.
- Keep sensitive detail proportionate to the formal purpose. Never expose another named
  rep's evidence; aggregate comparators when permitted.
- Use at least 50 pt for the deck title, 35 pt for slide titles, 24 pt for subheads, and
  16 pt for body copy. Shorten content or add an evidence appendix rather than shrinking
  text or allowing clipping.

### Preserve provenance in slides and notes

- Put a `[Sources]` block in speaker notes for every non-trivial claim, metric, and
  externally sourced asset. Name the Summit53 logical capability, retrieval/as-of date,
  window, comparator, evidence status, and warnings needed to interpret the slide.
- Keep interpretation-changing limits visible on the slide, not only in speaker notes.
- Treat the evidence-register appendix as audience-visible provenance; speaker notes do
  not replace it.
- If a DOCX companion is explicitly requested, create it from the same reconciled evidence
  and gate state after the PPTX, and verify it with the Documents skill.

## 5. Language rules

Ban verdict language: `underperformer`, `poor performer`, `failing`, `should be`,
`recommend`, `needs a PIP`, `unable to`, `lacks`, and unsupported causal phrases.

Write measurements instead:

- "Attainment is X% against the rep's segment benchmark of Y% for {window}."
- "Focus metric moved X → Y; the record does not establish why."
- "Discovery averaged X across N deals against the published playbook standard Y."
- "The ledger labels the movement 'worked'; it is correlational."

Check diagnostic `_evidence[metric].verified` before citing a value. A team-P75 benchmark
is aspirational, not a peer average; quote the returned warning and sample size. A
benchmark without a verified rep measurement is not a gap.

## 6. Verify before delivery

1. Confirm the primary artifact is `.pptx`, its filename follows the contract, and no
   standalone Markdown artifact was created by default.
2. Confirm evidentiary depth is slide 2 and structural factors precede performance evidence.
3. If the complete stop fired in a formal-use run, confirm the deck has only three or four
   slides and contains no performance, behaviour, attainment, pipeline, execution,
   qualification, or trajectory section in visible text or speaker notes. Permit a longer
   Staging demo only under the labelled demo-forward-test exception, with the formal stop
   result explicit on the gate slide.
4. If the partial gate fired, confirm the provisional label appears on every applicable
   downstream evidence slide. For every Staging forward test, confirm the demo label
   appears on every slide whether or not fixture data was used.
5. Search all visible text and speaker notes for banned verdict language; require zero hits.
6. Confirm every performance value has a named comparator, window, evidence status, source
   date, and source, and that the visible evidence register reconciles those claims.
7. Confirm every unavailable source is explicit and every ramp figure carries the survivor
   caveat in the same section.
8. Confirm assigned interventions are not described as coaching delivered, and that
   `null`, `[]`, `not_generated`, and unavailable capabilities are not rendered as zero.
9. Confirm no synthetic, fixture, or seeded record is presented as real employment evidence
   and no mutation capability was called.
10. Render every slide, inspect each at full size, and fix overlap, clipping, wrapping,
    unresolved placeholders, unreadable labels, exposed sensitive detail, and source/data
    mismatches. Run the Presentations skill's slide test and require no unintended errors.
11. Confirm body text is at least 16 pt, interpretation-changing limits are visible, and
    `[Sources]` notes are present for every evidence-bearing slide.

## Logical capabilities

| Capability | Role |
|---|---|
| `current_context` | Verify organization scope |
| `coaching_intervention_plan` | Roster, flag quality, persistence |
| `segment_performance_summary` | Territory comparator |
| `ramp_cohort` | Ramp and survivor disclosure |
| `hunter_farmer_mix` | Role–motion fit |
| `coaching_history` | Authoritative dated coaching-evidence timeline |
| `rep_coaching_context` | Bundled depth fallback |
| `coaching_development` | Diagnostic history, trajectory, goals |
| `coaching_meeting_analytics` | Recorded-meeting behaviour |
| `coaching_diagnostic`, `coaching_agenda` | Stored-record corroboration |
| `list_interventions`, `get_intervention_outcome` | Assigned interventions only |
| `forecast_confidence`, `pipeline_risk_summary` | Attainment and pipeline |
| `activity_gaps`, `deal_drag_dashboard`, `deal_drag_summary`, `team_action_plan` | Execution evidence |
| `opportunity_framework_summary`, `list_methodology_playbooks` | Qualification standard |
