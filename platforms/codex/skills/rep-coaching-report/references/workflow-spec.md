---
name: rep-coaching-report
description: "Generate a coaching-ready PPTX for a routine developmental 1:1 and optionally capture an explicitly approved session completion or later outcome. Use for recurring coaching preparation, follow-up, manager notes, action items, and questions such as 'what should I coach this rep on?'. Do not use for promotion, PIP, talent calibration, formal HR documentation, or employment decisions; use rep-evidence-dossier."
---

> **Codex compatibility notice:** Use this file for coaching logic, evidence requirements, fallbacks, narrative, slide content, and post-session field semantics. The parent `SKILL.md` overrides every legacy instruction about Claude, PptxGenJS, `pptxgenjs.md`, legacy rendering commands, or a generic outputs folder. Use Codex's available Presentations skill for implementation and QA, and perform a coaching-session write only under the parent skill's explicit-write rules.

# Rep Coaching Report

Generate a coaching-ready performance deck for a specific sales rep by pulling live data from Summit53 CRM tools and assembling it into a polished, actionable PPTX presentation.

## Contents

- [Identify the rep](#step-1-identify-the-rep)
- [Pull evidence](#step-2-pull-all-data)
- [Analyze patterns](#step-3-analyze-patterns)
- [Design and build](#step-4-build-the-deck)
- [Generate and verify](#step-5-generate-the-file)
- [Close the loop](#step-7-close-the-loop-post-session)

**Tools Used**: `current_context`, `coaching_diagnostic`, `coaching_agenda`, `coaching_history`, `coaching_intervention_plan`, `complete_coaching_session`, `record_coaching_outcome`, `forecast_confidence`, `risk_heatmap`, `pipeline_risk_summary`, `activity_gaps`, `opportunity_framework_summary`, `get_opportunity_notes_summary`, `get_opportunity_notes`, `get_opportunity_activities`, `get_opportunity_signals`, `deal_drag_dashboard`, `deal_drag_summary`, `team_action_plan`, `outreach_funnel_summary`, `search_outreach_leads`, `list_account_contracts`, `list_impact_entries`, `revenue_loop_diagnosis`, `hunter_farmer_mix`, `ramp_cohort`, and `list_methodology_playbooks`.

## Why This Exists

Sales managers spend hours prepping for 1:1s — pulling deal data, cross-referencing activity logs, trying to spot patterns. This skill does it in one shot: live CRM data flows into a professional coaching deck with specific, evidence-based recommendations. It turns data into coaching conversations.

## Step 1: Identify the Rep

Before pulling data, you need the rep's ID. Ask the user which rep they want a coaching report for, then:

1. Call `current_context` and require the intended organization and an authorized manager scope.
2. Resolve the rep from `coaching_intervention_plan` or an authorized coaching roster response. Do not infer identity from `search_accounts` or `search_opportunities`; deal search has no reliable rep-name filter.
3. Once the roster-provided user ID is confirmed, proceed to data pulls.

If the user says "just do it" or does not specify a rep, present the authorized coaching roster so they can pick one.

## Step 2: Pull All Data

Call these Summit53 MCP tools in parallel where possible. All rep-filtered calls use the `reps` parameter with the rep's user ID.

### Required Data Pulls

**Foundation — pull these first; they frame the report:**

- **Coaching diagnostic** — `coaching_diagnostic` with `rep_id: repId`. Returns the diagnosed coaching layer (Results/Effort/Knowledge/Skills/on_target/other), the single focus metric with highest improvement leverage, gap percentage vs team P75 benchmark, and signal-quality metadata. Honor `coaching_flag_quality` and `ordering`: suppress a non-discriminating flag and never calculate or display an ordinal rep rank when `ordinal_ranking` is false. This is a coaching hypothesis, not a verdict about the person.
- **Coaching agenda** — `coaching_agenda` with `rep_id: [repId]`. Returns the upcoming session context: `session_id`, `week_type` (Strategic / Skills / Career / Execution / Close), `coaching_model`, `scheduled_date`, the `diagnostic_summary`, and `previous_action_items` carried forward from the last 1:1. **Capture the `session_id`** — Step 7 will use it to close the loop post-session. Also note the `previous_action_items` — they belong on Slide 8 as accountability for prior commitments (distinct from CRM action-plan items).
- **Coaching history** — `coaching_history` with `rep_id: repId`. Use dated session lifecycle, notes, actions, provenance, acknowledgements, and outcome assessments as the authoritative delivered-coaching record. Inspect fixture/source markers; exclude `synthetic`, `demo_seed`, and `demo_fixture` rows from a real coaching deck. Label any Staging test that uses them **Demo data — not for real coaching**.

These two calls are cheap, can run in parallel, and together they answer "what should this coaching conversation actually be about?" before any deal-level evidence is pulled. If `coaching_agenda` returns "No active coaching cadence found", skip the agenda-dependent sections (session context footer, previous action items) and continue with just the diagnostic.

Additionally, pull these signals to cross-validate and contextualize the diagnosis before moving to deal-level evidence:

- **Revenue loop diagnosis** — `revenue_loop_diagnosis`. Its coaching lane independently names a priority rep and a failing layer (Results/Effort/Knowledge/Skills) using a different signal path than `coaching_diagnostic`. Pull it and compare: if it agrees with `coaching_diagnostic`'s diagnosed layer, that's corroboration — say so on Slide 2. If it disagrees (a different rep flagged as priority, or a different failing layer for this rep), don't silently trust one signal over the other — surface the tension on Slide 2 as an explicit note.
- **Hunter/farmer mix** — call `hunter_farmer_mix` at roster level with a supported window, then select `user_id == repId` client-side. Use it as a role-fit lens; do not pass an unsupported `rep_id` argument.
- **Ramp cohort** — call `ramp_cohort` at roster level and select `user_id == repId` client-side, **for newer reps only**. State the survivor-cohort limitation and never pass an unsupported `rep_id` argument.
- **Methodology playbooks** — `list_methodology_playbooks`. Pulls the org's own published MEDDPICC/BANT (or other) framework definitions — "what good looks like" per element, in this org's own language, rather than an implicit generic standard. This grounds Slides 5 and 6.

`revenue_loop_diagnosis`, `hunter_farmer_mix`, and `ramp_cohort` are **manager/team-permission gated** — if any returns an authorization error, skip that specific pull gracefully (omit the corresponding lens/callout on Slide 2) and continue with the rest of the foundation data. Don't block the report on them.

**Then pull deal-level evidence in parallel:**

1. **Rep Pipeline & Forecast**
   - `forecast_confidence` filtered by rep (`reps: [repId]`) — confidence score, deal count, pipeline value, velocity, quota coverage
   - `forecast_confidence` unfiltered — to get team averages for comparison

2. **Deal Risk Heatmap**
   - `risk_heatmap` filtered by rep (`reps: [repId]`, `page_size: 25`, sorted by `healthScore` ascending) — riskiest deals first. Treat `riskScore` as a deprecated alias, not an inverted risk metric.

3. **Pipeline Risk Distribution**
   - `pipeline_risk_summary` filtered by rep (`reps: [repId]`) — high/medium/low risk distribution for this rep

4. **Activity Gaps**
   - `activity_gaps` (`days: 30`, `owner_ids: [repId]`) — rep's accounts with no recent engagement

5. **Framework Analysis** (MEDDPIC by default)
   - For each of the rep's top deals (up to 8-10 from the risk heatmap), call `opportunity_framework_summary` with `framework: "MEDDPIC"` and the opportunity ID
   - These calls can be launched in parallel — they're independent

6. **Deal Narratives** (run in parallel with framework analysis)
   - For each of the rep's top deals (same set as framework analysis, up to 8-10), call `get_opportunity_notes_summary` with the opportunity ID
   - Also call `get_opportunity_notes` for the rep's top 3-5 risk deals to surface unresolved blockers and objections from recent notes
   - Also call `get_opportunity_activities` for the rep's highest-risk deals (top 3-5 by risk score) to assess cadence and last touch
   - Also call `get_opportunity_signals` for the rep's top 2-3 risk deals (a subset of the top 3-5 above) — pull the single first-constraint (the primary blocking factor Summit53's signal engine identifies for that deal) for use as a one-line coaching talking point on Slide 4
   - These add the qualitative "what's actually happening" layer that scores alone can't provide

7. **Deal Drag** (run in parallel)
   - `deal_drag_dashboard` filtered by rep (`reps: [repId]`) — waste scores per deal, staleness %, activity level, drag cause (political/technical/commercial/process), and recovery strategies
   - `deal_drag_summary` — summary totals for the rep: stalled deal count, avg waste score, risk distribution
   - This gives you the "cost of inaction" layer: a rep can look fine on risk scores but have $500K sitting completely dark for 30+ days

8. **Action Plan & Accountability** (run in parallel)
   - `team_action_plan` filtered by rep (`user_id: [repId]`) — action completion rates, missed deadlines, flagged items
   - This surfaces the rep's execution on previously assigned actions and closes the coaching feedback loop

9. **Outreach Health** (optional — include if rep manages outreach leads)
   - `outreach_funnel_summary` — overall funnel health, conversion velocity, stage distribution
   - `search_outreach_leads` filtered by rep (`owner_ids: [repId]`) — rep's outreach lead pipeline by stage
   - Use this to assess lead-generation health and flag conversion bottlenecks

10. **Renewal & Expansion Signals** (optional — include if org tracks post-sale value)
    - For the rep's top-value accounts, call `list_account_contracts` for each account ID — get upcoming renewal dates and contract status
    - For those contracts, call `list_impact_entries` to surface post-sale value achievements and expansion signals
    - This rounds out the coaching conversation with renewal risk and upsell opportunity visibility

11. **Delivered Coaching History**
    - Use `coaching_history(rep_id: repId)` for recommendations, plans, scheduled/completed sessions, manager attestations, notes, actions, acknowledgements, and later outcome assessments.
    - Keep each lifecycle claim distinct: planned is not delivered, delivered is not acknowledged, and an outcome assessment is not proof of causation.
    - Generic Intervention Ledger records may be owner-filtered client-side only as deal-execution accountability. Never describe them as coaching delivered.

### Handling Missing Data

Don't fail if data is sparse — adapt:
- If framework summaries return errors for some deals, skip them and note "Framework data unavailable" for those deals
- If activity gaps returns empty, that's a positive signal — note "No engagement gaps detected"
- If the rep has very few deals, the report will be shorter but still valuable
- If an optional tool is unavailable or unauthorized, label the affected block unavailable. Do not silently omit missing coaching history, fixture filtering, or organization scope.

## Step 3: Analyze Patterns

Before building slides, synthesize the raw data into coaching insights. This is what makes the report useful — not just numbers, but patterns and recommendations.

### Pattern Detection

1. **Framework Gaps**: Look across all MEDDPIC scores for the rep's deals. Which elements are consistently weak? For example, if 5 out of 7 deals score below 50% on "Paper Process", that's a coaching priority.

2. **Risk Concentration**: Is the rep's risk skewed toward a particular type? (e.g., mostly "No Champion" or mostly "Budget Uncertainty")

3. **Activity Patterns**: Compare the rep's engagement frequency to what's expected. Dormant accounts with active deals are a red flag. Use `get_opportunity_activities` results to check the cadence on highest-risk deals — if the last activity on a Commit-stage deal was 3 weeks ago, that needs to be in the coaching conversation.

4. **Qualitative Themes from Notes**: Scan the notes summaries across the rep's deals for recurring themes. Common signals to look for:
   - Pricing objections or procurement resistance appearing across multiple deals
   - Competitive threats (same competitor showing up in multiple deals)
   - Stalled next steps ("next step is to schedule X" appearing in old notes with no follow-through)
   - Single-threaded deals (notes only reference one contact)
   - Paper process issues mentioned but unresolved

5. **Deal Health Distribution**: What percentage of deals are high/medium/low risk? How does this compare to the team average?

6. **Deal Drag & Staleness**: From `deal_drag_dashboard`, how many of the rep's deals are stalled (activity_level: "stalled") vs low/medium/high? What is their average waste score vs the team average? Are there deals sitting in Negotiation or Proposal with high staleness — money that should have moved but hasn't? Note the drag cause (political/technical/commercial/process) for stalled deals — these inform the coaching angle.

7. **Pipeline Balance**: Is the rep over-indexed on a few large deals (concentration risk) or well-diversified?

8. **Ramp Context (newer reps only)**: If `ramp_cohort` was pulled, check whether apparent gaps are just normal ramp-stage variance before generating recommendations — don't recommend "fixing" a metric that's tracking within expected range for the rep's tenure cohort.

### Generate Coaching Recommendations

Based on the patterns above, generate 3-5 specific, actionable coaching recommendations. Each should:
- Reference specific evidence (e.g., "4 of your 6 deals have no identified economic buyer")
- Suggest a concrete action (e.g., "In your next call with Acme Corp, ask who signs the PO")
- Connect to a business outcome (e.g., "This is the #1 predictor of deals stalling in Stage 4")

Avoid generic advice like "improve discovery calls." Ground everything in the rep's actual data.

### Handling On-Target Reps

If `coaching_diagnostic` returned `diagnosed_layer` as `on_target` or `other`, the rep has no coaching gap this week. Adapt the deck rather than fabricating issues:

- **Shorten aggressively.** A 3–4 slide deck is better than a 10-slide one padded with invented problems. Top performers don't need a forced coaching narrative.
- **Slide 2** leads with positive reinforcement: "[Rep] is on-target across all four coaching layers this week". Still include the pipeline snapshot and session context footer.
- **Slides 3 and 4** (Deal Portfolio Health, Deal-Level Risk Detail) still render — even on-target reps benefit from a pipeline review.
- **Slides 5 and 6** (Framework gaps) — skip or collapse into a single "Framework strengths" slide that calls out the rep's strongest MEDDPIC elements as reinforcement of what's working.
- **Slide 8** — replace "Coaching Recommendations" with a single "What's working" slide highlighting 2–3 specific things the rep is doing well, with evidence. Still include the Previous Action Items section from the agenda if present — on-target reps still carry commitments forward.
- **Slide 9** — reframe as "Maintain momentum" with 2–3 forward-looking suggestions (expansion opportunities, stretch goals, areas to deepen) rather than gap-closing actions.

The goal is honest positive feedback grounded in data, not an empty deck and not a fabricated critique.

## Step 4: Build the Deck

Read the pptx skill's `pptxgenjs.md` reference for PptxGenJS technical details. Use the same **Midnight Executive** design system as the QBR generator for visual consistency.

### Design System

Use the exact same color palette, fonts, and helper functions from the QBR template the user provided. This ensures visual consistency across Summit53 deliverables.

| Role | Color | Hex |
|------|-------|-----|
| Primary (dark backgrounds) | Navy | `1E2761` |
| Secondary (light text, accents) | Ice Blue | `CADCFC` |
| Accent (highlights, positive) | Emerald | `10B981` |
| Warning | Amber | `F59E0B` |
| Danger | Red | `EF4444` |
| Text on dark | White | `FFFFFF` |
| Text on light | Charcoal | `1E293B` |
| Light background | Off-white | `F8FAFC` |
| Subtle border/divider | Slate | `64748B` |
| Light Slate (dividers, grid) | Light Slate | `E2E8F0` |

**Typography**: Georgia headers (36-44pt), Calibri body (14-16pt).
**Layout**: 16:9 widescreen. 0.5" margins minimum. Dark title/close slides, light content slides.

### Slide Structure

Build these slides in order. The deck is designed for a ~20 minute 1:1 coaching conversation.

---

#### Slide 1: Title Slide
- **Background**: Navy
- **Content**: "[Rep Name] — Coaching Report", date, "Powered by Summit53"
- **Layout**: Centered, clean. Large Georgia title, Calibri subtitle.

---

#### Slide 2: Coaching Diagnosis — This Week's Focus
- **Background**: Off-white
- **Data source**: `coaching_diagnostic` (rep-filtered), `coaching_agenda` (for session context), `forecast_confidence` (for supporting pipeline stats), `revenue_loop_diagnosis` (for cross-validation, if authorized), `hunter_farmer_mix` (for motion lens, if authorized), `ramp_cohort` (for newer reps, if authorized)
- **Purpose**: This slide is the thesis of the entire report. Every subsequent slide is evidence supporting or nuancing what's stated here.
- **Layout**:

  **Top half — the diagnosis (primary focus):**
  - Large centered callout showing the diagnosed layer as a colored badge. Colors: amber for `effort`, navy-on-ice-blue for `knowledge`, emerald for `on_target`, red for `results` (performance crisis), use a purple variant for `skills`. For `other`, use slate.
  - Below the badge: the focus metric name rendered in a readable form (e.g., `action_plan_completion` → "Action plan completion"), with current value, benchmark, and gap as a single line — "Currently 43%, benchmark 76%, gap 43.6%".
  - To the right of the focus metric line: render the returned signal-quality and benchmark context. Never hand-sort `composite_score` into "priority #N of M" when `ordering.ordinal_ranking` is false. Suppress the flag entirely when `coaching_flag_quality` is non-discriminating.
  - Directly below: one-sentence plain-English coaching hypothesis. Example: "The diagnostic identifies action-plan completion as the highest-leverage focus metric; discuss it alongside the evidence and the rep's context."
  - **Cross-validation against the revenue loop (if `revenue_loop_diagnosis` was pulled)**: if its coaching lane agrees with `coaching_diagnostic` on both the priority rep and the failing layer, add a small "confirmed by loop diagnosis" tag next to the diagnosis badge. If they disagree — a different rep flagged as priority, or a different failing layer for this rep — do not silently trust one signal over the other. Add a distinct callout (slate background, since this is a data tension, not a risk) stating both readings plainly, e.g.: "Note: revenue-loop diagnosis flags [Rep] under Effort, while the coaching diagnostic flags Results — worth surfacing both in conversation." Skip this cross-validation entirely if `revenue_loop_diagnosis` was unavailable or unauthorized.
  - **Motion lens (if `hunter_farmer_mix` was pulled)**: add a small inline note next to the diagnosis badge naming the rep's natural motion (e.g., "Natural motion: Hunter-leaning (72/28)"). If the diagnosed layer is `results` and the rep is strongly farming-oriented in a hunting-heavy territory (or vice versa), add a one-line reframe: "Consider whether this is a skill gap or a role-fit/territory mismatch" rather than assuming a training gap.
  - **Ramp context (newer reps only, if `ramp_cohort` was pulled)**: compare the rep's actual ramp curve to their cohort's expected curve. If the rep is within normal ramp variance, add a muted note under the diagnosis: "[Rep] is in month [N] of ramp — current metrics are tracking within [X]% of expected cohort pace" so the manager doesn't read normal ramp-stage softness as a standalone performance gap.

  **Bottom half — pipeline snapshot (supporting context):**
  - 4 compact stat cards (clearly visually smaller than the diagnosis block — these are evidence, not thesis):
    - Total Pipeline Value
    - Active Deal Count
    - Forecast Confidence Score
    - Average Deal Size
  - Below each, show team average for comparison
  - Colour: emerald above team average, amber below, red significantly below

  **Session context footer (small, muted, aligned to bottom-right):** If `coaching_agenda` returned a session, render its metadata — "Next 1:1 · Week [N] · [week_type_label] · [coaching_model_label] model · scheduled [date]". This anchors the report in the specific coaching conversation it's prepping for.

- **If `diagnosed_layer` is `on_target` or `other`**: skip the gap framing. Lead with an emerald positive callout — "[Rep] is on-target across all four coaching layers this week" — and keep the pipeline snapshot as supporting context. See "Handling On-Target Reps" below for how this changes the rest of the deck.

---

#### Slide 2b: Outreach Health (Optional)
- **Include only if rep manages outreach leads** — skip otherwise
- **Background**: Off-white
- **Data source**: `outreach_funnel_summary`, `search_outreach_leads` (rep-filtered)
- **Layout**: Top row — 4 stat cards: Total Leads, Leads by Stage (Created → Engaged → Qualified → Converted). Show conversion velocity (e.g., "8 qualified this period, 2 converted = 25% conversion rate"). Below — bar chart or table showing lead flow and stage distribution.
  - If conversion velocity is significantly below team average, flag with amber callout: "Lead conversion trailing team — consider review process or qualification criteria."
  - If velocity is strong, show as emerald: "Lead conversion on pace — maintain current funnel health."
- This slide is context-dependent; only render if the rep has measurable outreach lead responsibility.

---

#### Slide 3: Deal Portfolio Health
- **Background**: Off-white
- **Data source**: `pipeline_risk_summary` (rep-filtered), `risk_heatmap`
- **Layout**: Top row — 3 colored stat cards showing High/Medium/Low risk deal counts (using red/amber/emerald color bars on left edge). Below — doughnut chart showing risk distribution vs team average side by side (if team data available), or just the rep's distribution.
- Include the average risk score as a callout.

---

#### Slide 4: Deal-Level Risk Detail
- **Background**: Off-white
- **Data source**: `risk_heatmap` (rep-filtered), `deal_drag_dashboard` (rep-filtered), `get_opportunity_notes_summary` per deal, `get_opportunity_notes` for top deals, `get_opportunity_signals` for top 2-3 risk deals
- **Layout**: Table of all the rep's deals with columns: Deal Name, Amount, Stage, Risk Score, Waste Score, Activity Level. Sorted by waste score descending (stalled deals rise to the top). Color-code risk scores (red ≥70, amber 40-69, emerald <40) and waste scores (red ≥26, amber 15-25, emerald <15). Cap at 10 rows for readability.
- Below the table, show a "Deal Narratives" section: for the top 3 highest-risk/waste deals, include a one-line narrative excerpt from the notes summary.
- **New: "Blockers Requiring Action"** callout below narratives (amber background with amber left border): scan the most recent notes from top 3-5 risk deals for unresolved objections, stalled next steps, or unaddressed commitments. Display 2-3 specific blockers with dates, e.g.: "Pricing objection on Acme deal (noted 5 days ago) — needs manager escalation call" or "Decision timeline pending on TechCo — internal budget review, no date set". This gives concrete coaching talking points. Where available, prefix each of the top 2-3 risk deals' blocker lines with the single first-constraint from `get_opportunity_signals` (the primary blocking factor Summit53's signal engine flags for that deal), e.g.: "Champion risk is the blocking constraint on Acme — pricing objection noted 5 days ago compounds it." If `get_opportunity_signals` didn't return a first-constraint for a deal, fall back to the notes-derived blocker alone.
- Header row: Navy background, white text.

---

#### Slide 4b: Deal Drag Analysis
- **Background**: Off-white
- **Data source**: `deal_drag_dashboard` (rep-filtered), `deal_drag_summary` (rep-filtered)
- **Layout**: Top row — 3 stat cards: Stalled Deal Count (red if > 0), Total Pipeline Value Stalled ($), Avg Waste Score (vs team average).
- Below: For each stalled deal (activity_level: "stalled"), show a card with:
  - Deal name and amount
  - Days since last activity
  - Drag cause (political/technical/commercial/process) with a colored tag
  - Recommended recovery action from the dashboard
- Frame stalled deals as "revenue that has stopped moving" — concrete and actionable for the coaching conversation.
- If no stalled deals: show an emerald "No stalled deals — all pipeline is active" callout.

---

#### Slide 5: MEDDPIC Framework Analysis
- **Background**: Off-white
- **Data source**: `opportunity_framework_summary` results aggregated across deals, `list_methodology_playbooks` (for the org's own framework definitions)
- **Layout**: This is the key coaching slide. Show a horizontal bar chart or table with each MEDDPIC element (Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion, Paper Process) and the rep's average score across all deals.
  - Color each bar: emerald (≥70%), amber (40-69%), red (<40%)
  - Next to each element, note how many deals scored below 50% (e.g., "Paper Process — 5/7 deals below 50%")
  - Pull the org's own published MEDDPIC (or BANT, if that's the org's methodology) definitions via `list_methodology_playbooks` before rendering this slide. Use the org's own definition text for each element as a small subtitle under each element name (e.g., under "Champion" show the org's own one-line definition of what a validated champion looks like) instead of an implicit generic standard — this grounds "what good looks like" in the org's actual playbook. If `list_methodology_playbooks` returns nothing for the relevant framework, fall back to standard MEDDPIC element names without the org-specific definitions.
- If bar charts are complex, use a clean table with colored cells instead.

---

#### Slide 6: Weakest Framework Areas (Deep Dive)
- **Background**: Off-white
- **Data source**: `opportunity_framework_summary` — the 2-3 weakest MEDDPIC elements
- **Layout**: For the 2-3 lowest-scoring MEDDPIC elements, show deal-by-deal breakdown:
  - Which deals have gaps in this area?
  - What specific evidence is missing?
- Use a card layout: one card per framework element, each listing the deals where it's weak with the specific score.
- This gives the manager concrete talking points: "On the Acme deal, we don't have a champion identified yet — what's your plan?"

---

#### Slide 7: Activity & Engagement Patterns
- **Background**: Off-white
- **Data source**: `activity_gaps`, `get_opportunity_activities` (top 3-5 high-risk deals)
- **Layout**: If dormant accounts exist, show a warning callout (amber background, amber left border) with count. Below: table of dormant accounts with Account Name, Days Since Last Activity, and any active deal value at risk.
- Additionally, show a "Deal Cadence" section for the rep's highest-risk deals: for each, show the deal name, last activity date, activity type, and days since last touch. Flag any Commit or Negotiation-stage deals with no activity in 14+ days with a red indicator.
- If no gaps: show a green "All accounts engaged" callout instead — this is positive reinforcement.

---

#### Slide 8: Coaching Recommendations
- **Background**: Off-white
- **Data source**: `coaching_history`, `coaching_agenda.previous_action_items`, `team_action_plan` (rep-filtered CRM deal actions), plus synthesized recommendations from Step 3
- **Layout**:
  - **Top section — "Previous coaching commitments"**: Using `coaching_agenda.previous_action_items` from Step 2's foundation pull. These are the action items agreed in the last 1:1 via `complete_coaching_session` (see Step 7). Each item has a `task` and `completed` flag. Render as a short checklist — emerald check for completed, amber for outstanding. Example: "✓ Ringfence two 90-minute account-engagement blocks / ○ Draft 6-month development plan". If the list is empty, skip this section (first coaching session, or close-the-loop flow hasn't been used yet). **Do not conflate this with `team_action_plan` data below — they are two distinct streams.**
  - **Middle section — "CRM action plan — execution status"**: Using `team_action_plan` data, show completion rate (e.g., "Last period: 7 of 9 CRM actions completed (78%)"). If there are missed deadlines or flagged items, list them (e.g., "Missed: Follow up with Acme legal team, Update BrightCo proposal"). Frame this as deal-execution accountability — distinct from the coaching commitments above (those are about rep development; these are about deal movement).
  - **New section — "Documented coaching history"**: Render non-fixture `coaching_history` events in date order, keeping recommendation, plan, schedule, completion, acknowledgement, and later outcome claims distinct. An outcome may be described as recorded after coaching, never as caused by it. If no admissible history exists, say so rather than substituting deal interventions.
  - **Bottom section — 3-5 numbered coaching recommendations**, each with:
    - A bold headline (what to do)
    - A supporting sentence (why, with evidence)
    - If the "Coaching history" section above surfaced a prior attempt at this same gap, factor that into the relevant recommendation explicitly (e.g., propose a different approach rather than a repeat of an intervention that didn't stick)
  - Use numbered circles in emerald as bullet markers. Give each recommendation space — don't cram.
- This is the most important slide for the 1:1 conversation. "Previous coaching commitments" opens with continuity and accountability on what was agreed; "CRM action plan" shows deal-execution; "Coaching history" shows whether past coaching on this gap actually stuck; recommendations then move forward.

---

#### Slide 8b: Renewal & Expansion Signals (Optional)
- **Include only if org tracks renewals and post-sale value** — skip otherwise
- **Background**: Off-white
- **Data source**: `list_account_contracts` (rep's top accounts), `list_impact_entries` (per contract)
- **Layout**: Top row — 2-3 stat cards: Upcoming Renewals (next 90 days), At-Risk Contracts, Expansion Opportunities Identified. Below — table showing top accounts with Contract Status, Renewal Date, Post-Sale Impact Score, and Expansion Signals.
  - For each contract, list 1-2 specific post-sale value achievements or expansion hooks, e.g.: "Customer reduced deployment time by 30% — upsell candidate for consulting services" or "Contract renews Q3 — at-risk due to competing RFP."
  - Color-code renewal risk: red for at-risk, emerald for healthy/expansion-ready.
- This slide rounds out the coaching conversation by surfacing renewal risk and expansion upside for the rep's book.

---

#### Slide 9: Focus Areas for Next Week
- **Background**: Off-white
- **Data source**: Synthesized from all data — specific actions for the coming week
- **Layout**: 3-5 specific, time-bound actions. Each should reference a specific deal or account. Format as a checklist-style layout:
  - "Schedule champion identification call with Acme Corp (Deal: $450K, Risk: 85)"
  - "Re-engage GhostInc — 62 days dormant, $85K ARR at risk"
  - "Update decision criteria documentation on TechCo deal before Thursday"

---

#### Slide 10: Closing Slide
- **Background**: Navy
- **Content**: "Let's make this the best quarter yet.", company name, date
- **Layout**: Clean, centered, motivational. Mirror the title slide design.

---

## Step 5: Generate the File

Write a complete Node.js script using PptxGenJS that:

1. Embeds all the pulled data directly (no external data files)
2. Uses the same helper functions as the QBR template (addStatCard, addSectionTitle, riskColor, formatCurrency, etc.)
3. Constructs all slides following the structure above
4. Handles edge cases (missing data, empty arrays, zero values)
5. Saves to the outputs folder as `Rep-Coaching-Report-[RepName]-[Date].pptx`

Use factory functions for shadows and card styles to avoid PptxGenJS's object mutation issues (same pattern as the QBR template).

## Step 6: QA

After generating the file:

1. Convert to images:
   ```bash
   python scripts/office/soffice.py --headless --convert-to pdf output.pptx
   pdftoppm -jpeg -r 150 output.pdf slide
   ```
2. Visually inspect every slide for overlapping text, missing data, color contrast issues
3. Verify data accuracy — spot-check that numbers match what the MCP tools returned
4. Fix issues and re-verify

## Tips for Great Coaching Reports

- **Be specific, not generic.** "Improve discovery" is useless. "Ask Acme Corp's VP of Eng who approves the budget" is coaching.
- **Balance positive and constructive.** Start with what's going well before diving into gaps.
- **Ground recommendations in data.** Every suggestion should trace back to a specific metric, score, or pattern.
- **Make it conversational.** The deck should spark discussion, not deliver a verdict. Frame gaps as opportunities: "Here's where the biggest upside is hiding."
- **Keep it short.** 10 slides max. The 1:1 should be a conversation, not a presentation marathon.

---

## Step 7: Close the Loop (Post-Session)

**This step runs after the 1:1 has happened** — typically hours or days after Steps 1–6, in a separate conversation. It turns the one-shot report into a persistent coaching thread: action items captured here flow into the next session's `previous_action_items`, giving subsequent coaching conversations continuity.

This step is **optional** — not every coaching report gets closed out via this flow. But when it is used, it's what makes the coaching loop actually close.

### Trigger Phrases

"log my notes from the session with [Rep]", "close out the [Rep] 1:1", "record the action items from my coaching session with [Rep]", "complete coaching session for [Rep]", "save my 1:1 notes", "log action items for [Rep]".

### Workflow

Both `complete_coaching_session` and `record_coaching_outcome` are approval-gated writes.
Do not call either without an explicit user request and a valid approval receipt. Session
completion records what occurred; a later outcome assessment is a separate audit event.

1. **Retrieve the session_id**. Either:
   - Use the `session_id` captured in Step 2's `coaching_agenda` call (if the skill's context still holds it from the earlier report generation)
   - Or re-pull `coaching_agenda(rep_id)` — it will return the same current-week session, typically still `status: scheduled` if the session is being closed promptly after the 1:1
   - If the returned session is already `status: completed`, stop and tell the manager — this session has already been closed. Don't silently overwrite. Ask whether they meant a different session.

2. **Gather notes and action items conversationally**. Don't demand structured input. Typical flow:
   - "What came out of the session — any key takeaways or observations?"
   - "What did you and [Rep] agree as action items?"
   - If the manager gives vague notes, reflect and sharpen: "Improve discovery" → "Record and review one discovery call before Thursday's sync".

3. **Inspect the live schema and current session state.** If the user asked to complete
   the session, call `complete_coaching_session` once with the required manager
   attestation, occurred/completed timestamps, notes, action items, evidence/provenance,
   idempotency key, and approval receipt supported by the exposed schema. Never guess a
   receipt or re-complete an existing session.

4. **Confirm back to the manager** in conversational prose: the count of action items recorded and a note that they'll appear as `previous_action_items` in the next session's agenda. Don't read the items back verbatim unless the manager asks — they just dictated them.

5. **Record a later outcome only on a separate explicit request.** Call
   `record_coaching_outcome` only for a completed session, with the exposed outcome
   status, assessment date, evidence, notes, follow-up date, idempotency key, and approval
   receipt. Never treat completion as an outcome or infer an outcome from pipeline movement.

### Guidance on Good Action Items

When helping the manager draft action items, steer toward items that are:

- **Specific** — "Pair-qualify 5 new ICP accounts before next 1:1" not "improve qualification"
- **Time-bound** — include a check-in point or deadline where realistic
- **Evidence-generating** — the item should produce something observable by the next session (a completed task, a metric shift, a recorded call, a document)
- **Owned** — it's clear whether the rep or the manager is driving it

If the manager provides items that don't meet these criteria, offer a sharpened version and let them approve or edit. Don't lecture — one or two suggestions, then respect their judgment.

### Edge Cases

- **No session found** — if `coaching_agenda` returns "No active coaching cadence found for rep", tell the manager the rep doesn't have a scheduled session to close out. Offer to draft the notes as a standalone PerformanceNote (if and when a write tool supports that directly), otherwise direct them to the Coaching dashboard at `/coaching` to set up a cadence.
- **Session already completed** — stop and surface this to the manager rather than overwriting. The endpoint's re-completion behavior isn't guaranteed and silent overwrites would lose coaching continuity.
- **Partial information** — if the manager only has notes without action items (or vice versa), pass only what's provided. The endpoint accepts empty strings for either field.
- **No explicit approval** — produce a structured completion or outcome draft and state that nothing was saved.

### What This Unlocks

Once this step runs, the next time Step 1–6 runs for this rep, `coaching_agenda.previous_action_items` will contain these items — and they should appear on Slide 8 as the accountability header. That's the continuity loop: report → 1:1 → close → next report carries forward the commitments. Managers and reps arrive at every 1:1 already knowing what was agreed last time, without having to remember.
