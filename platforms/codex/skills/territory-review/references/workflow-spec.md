---
name: territory-review
description: "Generate a territory planning and review deck as a polished PPTX presentation. Pulls account intelligence, pipeline distribution, health scores, activity gaps, and ARR data from Summit53 CRM tools to produce a strategic territory analysis — identifying whitespace, underperforming territories, expansion opportunities, and rebalancing recommendations. Use this skill whenever anyone asks for a territory review, territory planning, territory analysis, geo review, regional performance review, territory scorecard, whitespace analysis, territory rebalancing, or strategic territory planning. Also trigger on phrases like 'how are my territories doing', 'territory breakdown', 'where should we prospect', 'which territories are underperforming', 'territory health check', 'regional pipeline review', or 'show me territory coverage'."
---

> **Codex compatibility notice:** Use this file for domain logic, evidence requirements, fallbacks, territory analysis, narrative, slide content, and visual intent. The parent `SKILL.md` overrides every legacy instruction about Claude, PptxGenJS, `pptxgenjs.md`, legacy rendering commands, or a generic outputs folder. Use Codex's available Presentations skill for implementation and QA.

# Territory Review

Generate a strategic territory planning deck by pulling live data from Summit53 CRM tools and assembling it into a polished, actionable PPTX presentation that reveals where to double down, where the whitespace is, and which territories need attention.

## Why This Exists

CROs and VPs managing multiple territories or regions need a clear picture of how each territory is performing — not just in revenue, but in pipeline health, account engagement, risk distribution, and growth potential. Building this view manually means hours of cross-referencing dashboards. This skill does it in one shot: live CRM data flows into a strategic territory planning deck with specific, evidence-based recommendations for territory optimization.

## Step 1: Clarify Scope

Before pulling data, confirm these with the user (use sensible defaults if they say "just do it"):

- **Territories of interest**: All territories, or specific ones? Default to all.
- **Time period**: Current quarter? Current + previous for comparison? Default to current quarter.
- **Audience**: CRO/board (strategic, high-level) or regional managers (operational detail)? Default to CRO.
- **Special focus**: Any specific territories, segments, or accounts to highlight?

## Step 2: Pull All Data

Call these Summit53 MCP tools in parallel where possible. The goal is to get territory-level breakdowns across revenue, pipeline, health, and engagement.

### Required Data Pulls

1. **Account Intelligence by Territory**
   - `account_intelligence_summary` — this is the primary data source. Returns territory_summary, value_segments, health_distribution broken down by territory. Call without filters first to get the full picture.
   - If specific territories are requested, also call with `territories: [list]` to get filtered views.

2. **Pipeline Risk Distribution**
   - `pipeline_risk_summary` — pipeline value distribution, risk levels, confidence metrics across the entire book
   - Optionally filter by territory if the tool supports it

3. **Deal-Level Risk Heatmap**
   - `risk_heatmap` — deal-level health scores, health bands, framework scores, and risk factors (`page_size: 25`, `sort_by: "healthScore"`, `sort_direction: "asc"`)
   - This gives you the specific deals that are driving risk in each territory

   Treat `score_semantics` as authoritative: `healthScore` is higher-is-healthier and riskiest-first is ascending. `riskScore` is only a deprecated alias of `healthScore`; never sort it descending. Prefer each row's `healthBand` over hand-rolled thresholds.

4. **Activity Gaps**
   - `activity_gaps` — dormant accounts (days: 30, limit: 25). These map to territories via the account data.
   - Dormant accounts in high-value territories are particularly concerning

5. **ARR Growth**
   - `arr_growth_analytics` — total ARR, net retention rate, growth stage, benchmarks
     - Set `include_trends: true`, `include_changes: true`, `include_benchmarks: true`
   - This provides the revenue foundation for territory analysis

6. **Forecast Data**
   - `unified_forecast_summary` — pipeline coverage, quota tracking, team metrics
     - Current period: `period_offset: 0`
     - Also returns `kpis.pipeline_coverage.by_deal_size` (org-adaptive deal-size bands — pipeline value per band), `kpis.win_rate.by_deal_size` (win rate per band), and `kpis.pipeline_coverage.acv_drift` (`drift_pct`, `direction`, `is_significant`). Deal-size mix is a useful territory-strategy lens — territories skewed entirely to one band carry different risk than balanced ones.
     - This tool is asynchronous on a cold cache. Follow `references/async-envelopes.md`: poll `get_job` to terminal, then re-call with identical arguments for the payload. Resolve it once and reuse the payload across the deck.
   - `forecast_confidence` — confidence scores, rep performance, velocity, stage distributions

7. **Capacity vs. Target (Scorecard Verdict)**
   - `capacity_to_target_planner` — grouped by `team` and/or `sales_role` — assesses whether each territory's current staffing can realistically hit target, and separates territories that are capacity-constrained (not enough reps) from those that are execution-constrained (enough reps, target still at risk). Feeds the Territory Scorecards (Slide 3).
   - Manager/team-permission gated. If the call is unauthorized or empty, omit the capacity verdict from the scorecards rather than failing.

8. **Reverse Capacity Planning (Intervene Recommendations)**
   - `reverse_capacity_planner` — grouped by `team` and/or `sales_role` — converts an "Intervene" territory's gap-to-target into a concrete headcount ask (e.g., "West needs ~1.4 more AEs to hit target"). Feeds Slide 9 Territory Recommendations.
   - Manager/team-permission gated. If unauthorized or empty, fall back to qualitative effort-shift language for Intervene recommendations rather than failing.

9. **Renewal Forecast (Defense)**
   - `renewal_forecast_summary` — ARR renewing in the next 30-180 days and at-risk renewals, ideally broken down by territory. This is the defense counterpart to the new-pipeline data pulled in item 6 above — without it, the deck only covers offense. Feeds Slide 4 Pipeline Distribution.
   - Manager/team-permission gated. If unauthorized or empty, note "Renewal defense data not available — showing new pipeline only" and proceed with new-pipeline data alone.

10. **Ramp Cohort**
    - `ramp_cohort` — identifies reps who are still inside their ramp window. Use this to sanity-check territory performance before labeling a territory "underperforming" — a territory staffed with recently-ramping reps should be judged against ramp-stage expectations, not full-quota expectations. Feeds Territory Scoring (Step 3) and the framing on Slide 3 and Slide 9.
    - Manager/team-permission gated. If unauthorized or empty, proceed with standard performance framing and skip the ramp adjustment.

11. **Hunter/Farmer Mix**
    - `hunter_farmer_mix` — per-territory new-business vs. expansion deal mix. Reveals whether flat territory growth is a hunting problem (not enough new logos) or a farming problem (not enough expansion in the existing base). Feeds Slide 6 Whitespace Analysis.
    - Manager/team-permission gated. If unauthorized or empty, fall back to the existing whitespace/expansion framing without the hunter/farmer split.

12. **Account Health Movement**
    - `account_health_movement` — trended account health per territory, i.e. accounts moving healthy → at-risk (and at-risk → critical, or back to healthy) over the period. Replaces a static point-in-time health snapshot with a trend, which catches deteriorating territories a snapshot alone would miss. Feeds Slide 5 Account Health by Territory.
    - Manager/team-permission gated. If unauthorized or empty, fall back to the static `health_distribution` snapshot from `account_intelligence_summary`.
    - Movement here is **correlational, not causal** — describe accounts as having "trended" or "moved" toward at-risk, never as something the territory or a rep "caused."

### Handling Missing Data

Territory data richness varies. Don't fail — adapt:
- If `account_intelligence_summary` doesn't return territory breakdowns, group accounts by whatever segmentation is available (industry, owner, size tier) and note "Territory-level segmentation not configured — showing account segments instead."
- If ARR growth has no territory breakdown, show the aggregate and note it applies company-wide.
- If activity gaps returns empty, that's a positive signal — note "No engagement gaps detected across territories."
- If a territory has zero accounts or zero pipeline, that IS the insight — it's whitespace.
- `capacity_to_target_planner`, `reverse_capacity_planner`, `renewal_forecast_summary`, `ramp_cohort`, `hunter_farmer_mix`, and `account_health_movement` are all manager/team-permission gated. If any of these calls comes back unauthorized or empty, fall back to the current tools/notes described above (scorecard fields without a capacity verdict, qualitative effort-shift language, new-pipeline-only view, standard performance framing, static health snapshot, two-column whitespace view without the hunter/farmer split) rather than failing the deck.

## Step 3: Analyze Territory Patterns

Before building slides, synthesize the raw data into strategic territory insights. This analysis is what makes the deck valuable — not just numbers, but patterns and recommendations.

### Territory Scoring

For each territory, compute a composite health view:

1. **Revenue Concentration**: What percentage of total ARR does this territory represent? Are we over-indexed on one territory?
2. **Pipeline Coverage**: How much pipeline exists relative to quota or target for each territory? Which territories are pipeline-starved?
3. **Account Health Distribution**: What's the healthy vs at-risk vs critical split per territory?
4. **Engagement Health**: How many dormant accounts per territory? What ARR is at risk from disengagement?
5. **Risk Density**: What's the average deal risk score per territory? Which territories carry the most high-risk deals?
6. **Capacity vs. Execution**: Use `capacity_to_target_planner` to separate territories that can't hit target because they're understaffed (capacity-constrained) from those with enough capacity that aren't executing (execution-constrained) — these two situations call for very different recommendations (headcount vs. coaching).
7. **Ramp-Adjusted Performance**: Cross-check apparent underperformers against `ramp_cohort`. A territory carrying multiple reps still inside their ramp window should be judged against ramp-stage expectations, not full-quota expectations — don't brand it "underperforming" until you've controlled for ramp.

### Whitespace Analysis

Identify territories with:
- Zero or minimal revenue but high market potential
- Low account counts relative to market size
- No active pipeline despite existing accounts
- Healthy accounts with no expansion motion underway

### Strategic Recommendations

Based on the patterns above, generate 3-5 territory-level strategic recommendations. Each should:
- Reference specific territory data (e.g., "West territory has 35% of accounts but only 18% of pipeline")
- Suggest a concrete action (e.g., "Rebalance prospecting effort — shift 2 SDR hours/week from East to West"). For **Intervene** recommendations specifically, prefer a concrete headcount ask from `reverse_capacity_planner` over vague effort-shift language when the tool is available (see Slide 9).
- Connect to a business outcome (e.g., "Closing the pipeline coverage gap in West could add $1.2M to Q3 forecast")

Avoid generic advice like "improve territory coverage." Ground everything in the actual data.

## Step 4: Build the Deck

Read the pptx skill's `pptxgenjs.md` reference for PptxGenJS technical details. Use the **Midnight Executive** design system for visual consistency with other Summit53 deliverables.

### Design System

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

Build these slides in order. The deck is designed for a ~25 minute strategic territory review.

---

#### Slide 1: Title Slide
- **Background**: Navy (`1E2761`)
- **Content**: "Territory Review", quarter/period label, date, "Powered by Summit53"
- **Layout**: Centered, clean. Large Georgia title, Calibri subtitle.

---

#### Slide 2: Territory Overview
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `account_intelligence_summary` (territory_summary), `unified_forecast_summary`
- **Layout**: 4 stat cards across the top row:
  - Total Territories Active
  - Total Accounts Under Management
  - Total Pipeline Value
  - Aggregate ARR
- Below: a summary table or card grid showing each territory with key metrics (account count, pipeline value, ARR, health score). Use color-coded left borders on each territory card (emerald for healthy, amber for needs attention, red for critical).

---

#### Slide 3: Territory Scorecards
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `account_intelligence_summary` (territory_summary, health_distribution), `capacity_to_target_planner` (capacity verdict), `ramp_cohort` (ramp guard)
- **Layout**: One scorecard card per territory (2x2 or 2x3 grid depending on territory count). Each card contains:
  - Territory name (bold header)
  - Account count
  - Pipeline value
  - Revenue / ARR
  - Health score (color-coded: emerald/amber/red)
  - Active deal count
  - **Capacity verdict**: a small badge from `capacity_to_target_planner` — "On Track to Hit Target," "Capacity-Constrained" (not enough reps to reach target even at full productivity), or "Execution-Constrained" (enough capacity, target still at risk — a coaching issue, not a headcount issue). If the tool is unauthorized or empty, omit the badge rather than guessing.
- If there are more than 6 territories, show the top 6 by ARR and note how many additional territories exist below.
- Before flagging a territory's health score or capacity verdict as concerning, check `ramp_cohort` for that territory. If a meaningful share of its reps are still ramping, note it on the card (e.g., "2 of 4 AEs ramping — attainment tracking to ramp plan") instead of flagging it red outright.

---

#### Slide 4: Pipeline Distribution by Territory
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `unified_forecast_summary`, `forecast_confidence`, `pipeline_risk_summary`, `renewal_forecast_summary` (defense)
- **Layout**: Horizontal stacked bar chart or grouped bar chart showing pipeline value per territory, broken down by stage or risk level. Below the chart: pipeline coverage ratio per territory as a simple comparison table (Territory | Pipeline | Target | Coverage Ratio).
- Highlight territories with coverage below 2x in red, 2-3x in amber, 3x+ in emerald.
- **Deal-size composition**: Add a "Pipeline by Deal Size" mini-chart from `kpis.pipeline_coverage.by_deal_size` showing the book's distribution across deal-size bands. A territory analysis benefits from this lens — coverage that looks healthy in aggregate may be concentrated in a single band, which affects how rebalancing recommendations should be framed (Slide 9). If `kpis.pipeline_coverage.acv_drift.is_significant` is `true`, add a one-line amber note: "Pipeline ACV is drifting {direction} {drift_pct}% vs trailing-12-month closed-won — pipeline deals no longer resemble what the team has historically closed." Omit when not significant.
- **Renewal defense**: Pull `renewal_forecast_summary` and add a compact "Renewal Defense" panel beneath the coverage table — ARR renewing in the next 30-180 days and at-risk renewal ARR, per territory. This is the deck's defense counterpart to the new-pipeline numbers above; a territory can look strong on new pipeline (offense) while carrying significant renewal risk (defense) that the coverage ratio alone won't show. If the tool is unauthorized or empty, note "Renewal defense data not available — showing new pipeline only" and proceed.

---

#### Slide 5: Account Health by Territory
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `account_health_movement` (primary — trended health by territory), `account_intelligence_summary` (health_distribution by territory, static snapshot / fallback)
- **Layout**: Lead with the movement view from `account_health_movement` — accounts that trended healthy → at-risk (and at-risk → critical) per territory over the period, since this catches deteriorating territories that a single-point-in-time snapshot misses. Pair it with the existing stacked bar chart or grouped stat cards showing Healthy / At-Risk / Critical account distribution per territory. Below: table of the top 5 at-risk accounts across all territories with Account Name, Territory, Health Score, ARR, and Primary Risk Factor.
- Describe movement as accounts having "trended" or "moved" toward at-risk/critical — this is correlational, not causal. Never say a territory or rep "caused" the movement; say accounts "moved" or "trended" that direction.
- `account_health_movement` is manager/team-permission gated. If the call is unauthorized or empty, fall back to the static `health_distribution` snapshot alone and note "Health movement data not available — showing point-in-time snapshot."
- This slide answers: "Where are our accounts most vulnerable — and which territories are trending in the wrong direction?"

---

#### Slide 6: Whitespace Analysis
- **Background**: Off-white (`F8FAFC`)
- **Data source**: Synthesized from all data pulls — territories with zero/low revenue, underserved segments; `hunter_farmer_mix` for deal-mix enrichment
- **Layout**: Two-column layout.
  - **Left column**: "Untapped Territories" — territories or segments with zero or minimal revenue. Show market indicators if available (account count with no deals, large accounts with no engagement).
  - **Right column**: "Expansion Opportunities" — existing territories where healthy accounts have room to grow. Pull from expansion candidates in account_intelligence_summary.
- Use emerald accent on the expansion column, navy accent on the whitespace column.
- **Hunter/farmer enrichment**: Below the two columns, add a compact per-territory strip from `hunter_farmer_mix` showing the new-business vs. expansion deal split. This diagnoses *why* a territory is flat — a territory with strong hunting (new logos) but weak farming (expansion) needs a different play than the reverse, and this distinction should inform which column (or both) a territory lands in. If `hunter_farmer_mix` is unauthorized or empty, drop this strip and keep the two-column whitespace/expansion view as-is.

---

#### Slide 7: Engagement Gaps by Territory
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `activity_gaps`
- **Layout**: If dormant accounts exist, show a warning callout (amber background) with total count and total ARR at risk. Below: table of dormant accounts grouped by territory with Account Name, Territory, Days Since Last Activity, and ARR at Risk.
- If no gaps: show a green "All territories actively engaged" callout — this is positive reinforcement.
- Highlight which territories have the most dormant accounts.

---

#### Slide 8: Risk Heatmap by Territory
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `risk_heatmap`, `pipeline_risk_summary`
- **Layout**: Table of highest-risk deals, grouped or annotated by territory. Columns: Deal Name, Territory, Amount, Stage, Health Score, Health Band, Top Risk Factor. Color-code the server-supplied `healthBand`: `Low` → red, `Medium` → amber, `High` → emerald. Keep the table ordered by `healthScore` ascending.
- Cap at 10 rows for readability. Navy header row, white text.
- Below the table: a summary callout showing which territory carries the highest aggregate risk.

---

#### Slide 9: Territory Recommendations
- **Background**: Off-white (`F8FAFC`)
- **Data source**: Your synthesized recommendations from Step 3; `reverse_capacity_planner` for Intervene recommendations
- **Layout**: 3-5 numbered strategic recommendations, each with:
  - A bold headline (the action)
  - A supporting sentence (the evidence and expected impact)
- Use numbered circles in emerald as bullet markers. Give each recommendation space.
- Frame recommendations in three categories: **Double Down** (territories performing well), **Intervene** (territories needing attention), **Explore** (whitespace opportunities).
- For every **Intervene** recommendation, call `reverse_capacity_planner` (grouped by `team` and/or `sales_role`) and translate the recommendation from vague effort-shift language into a concrete headcount ask — e.g., "West needs ~1.4 more AEs to hit target" instead of "shift 2 SDR hours/week from East to West." If the tool is unauthorized or empty, fall back to the qualitative effort-shift language shown in the Step 3 example.

---

#### Slide 10: Closing Slide
- **Background**: Navy (`1E2761`)
- **Content**: "Territory Strategy: Where We Play, How We Win", company name, date
- **Layout**: Clean, centered. Mirror the title slide design.

---

## Step 5: Generate the File

Write a complete Node.js script using PptxGenJS that:

1. Embeds all the pulled data directly (no external data files)
2. Uses factory functions for shadows and card styles to avoid PptxGenJS's object mutation issues
3. Creates helper functions: `addStatCard()`, `addSectionTitle()`, `riskColor()`, `formatCurrency()`, `healthColor()`, `territoryCard()`
4. Constructs all slides following the structure above
5. Handles edge cases (missing data, empty arrays, zero values, missing territory breakdowns)
6. Saves to the outputs folder as `Territory-Review-[Date].pptx`

### Helper Function Patterns

```javascript
// Risk color coding
function riskColor(score) {
  if (score >= 70) return "EF4444";
  if (score >= 40) return "F59E0B";
  return "10B981";
}

// Health color coding
function healthColor(status) {
  const map = { healthy: "10B981", "at-risk": "F59E0B", critical: "EF4444" };
  return map[status?.toLowerCase()] || "64748B";
}

// Coverage ratio color
function coverageColor(ratio) {
  if (ratio >= 3) return "10B981";
  if (ratio >= 2) return "F59E0B";
  return "EF4444";
}

// Factory for shadows (avoid PptxGenJS mutation issue)
const makeShadow = () => ({ type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.15 });

// Format currency
function formatCurrency(val) {
  if (val >= 1e6) return `$${(val / 1e6).toFixed(1)}M`;
  if (val >= 1e3) return `$${(val / 1e3).toFixed(0)}K`;
  return `$${val}`;
}
```

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

## Tips for Great Territory Reviews

- **Lead with the strategic question.** Every slide should answer "where should we allocate resources?" not just "here are numbers by territory."
- **Make whitespace actionable.** Don't just say "Territory X has no revenue" — show what accounts exist there, what the potential is, and what it would take to activate it.
- **Balance defense and offense.** Show both where to protect (at-risk territories, and renewal risk from `renewal_forecast_summary`) and where to attack (whitespace and expansion). Don't let defense stay a vague gesture while offense gets hard numbers — quantify both sides.
- **Be honest about concentration risk.** If 80% of ARR comes from one territory, that's the most important insight in the deck.
- **Don't penalize ramp.** A territory staffed with recently-ramping reps isn't automatically "underperforming" — check `ramp_cohort` before you brand it that way.
- **End with clear territory actions.** The audience should leave knowing exactly which territories to invest in, which to defend, and which to explore. For Intervene territories, make the ask concrete — a headcount number beats a vague effort-shift.
- **Keep it short.** 10 slides max. The review should spark strategic discussion, not drown in data.
