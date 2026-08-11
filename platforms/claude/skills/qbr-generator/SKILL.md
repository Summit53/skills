---
name: "qbr-generator"
description: "Create an internal Summit53 quarterly revenue or sales review as an executive PPTX, with an optional DOCX companion. Use for quarterly operating reviews and executive performance decks. Despite the legacy name, do not use this for a customer-facing QBR; that external CS hot seat is a separate planned skill."
version: "1.0.0"
baselined: "2026-08-07"
status: "active"
---
---
name: qbr-generator
description: "Generate a complete Quarterly Business Review (QBR) deck or document by pulling live data from Summit53 CRM tools and assembling a polished, narrative-driven PPTX or DOCX deliverable. Use this skill whenever the user asks for a QBR, quarterly business review, quarterly review deck, executive revenue review, board deck with pipeline data, quarterly sales review, or any request to compile CRM performance data into a presentation or report. Also trigger when the user says things like 'prep for my QBR', 'build my quarterly deck', 'pull together the numbers for this quarter', or 'I need a revenue review'."
---

> **Codex compatibility notice:** Use this file for domain logic, evidence requirements, fallbacks, narrative, slide/document content, and visual intent. The parent `SKILL.md` overrides every legacy instruction about Claude, PptxGenJS, the old pptx/docx skills, legacy rendering commands, or a generic outputs folder. Use Codex's available Presentations skill and, only when requested, Documents skill for implementation and QA.

# QBR Generator

Generate a complete Quarterly Business Review by pulling live data from Summit53 CRM tools and assembling a polished, narrative-driven PPTX deck (default) or DOCX document.

## Why This Exists

Every revenue leader does QBRs, and building them is painful — hours of pulling data from dashboards, formatting slides, writing narratives. This skill does it in one shot: live CRM data flows into a professional, story-driven deliverable.

## Tools Reference

This skill uses the following Summit53 MCP tools:

**Revenue & Forecast**: `unified_forecast_summary` (incl. revenue per rep, win rate & coverage by deal size, ACV drift), `get_job`, `forecast_confidence`, `hunter_farmer_mix` (optional, manager/team-permission gated — rep deal-mix: net-new hunting vs expansion farming)

> **Async contract:** each `unified_forecast_summary` period can return a processing envelope. Follow `references/async-envelopes.md`: poll that call's `job_id` with `get_job` until terminal, then re-call the original tool with identical arguments for the payload. Current and prior periods are separate jobs. Never render a processing envelope as blank or zero data.

**ARR Growth**: `arr_growth_analytics` (incl. GRR, logo churn, time-to-value), `arr_growth_narrative`, `renewal_forecast_summary` (manager/team-permission gated — forward-looking renewal risk: ARR renewing in 30-180 days, at-risk causes, commit/best-case bands)

**Account Intelligence**: `account_intelligence_summary`, `account_health_movement` (current vs prior snapshot — correlational health trend, not a static snapshot)

**Pipeline Risk & Efficiency**: `pipeline_risk_summary`, `risk_heatmap`, `deal_drag_summary`, `deal_drag_dashboard`, `revenue_loop_diagnosis` (optional, manager/team-permission gated — first failing Figure-Eight stage, a process-level lens)

**Engagement**: `activity_gaps`

**Deal Deep-Dives**: `get_opportunity`, `get_opportunity_notes_summary`, `opportunity_framework_summary` (MEDDPIC/BANT/SPICED qualification context)

**Team Performance**: `team_action_plan`

**Post-Sale Health**: `get_value_impact_card` (optional)

**Action Planning**: `weekly_action_plan`

## Step 1: Clarify Scope

Before pulling data, confirm these with the user (use sensible defaults if they say "just do it"):

- **Period**: Which quarter? Default to current quarter.
- **Format**: PPTX deck (default) or DOCX document.
- **Audience**: Board/exec (high-level narrative) or sales leadership (operational detail). Default to exec.
- **Specific focus areas**: Any accounts, reps, or segments to highlight?
- **Comparison period**: Compare to previous quarter? Default yes.

## Step 2: Pull All Data

Call these Summit53 MCP tools. Launch as many in parallel as possible — they're independent. Capture the raw responses; you'll synthesize them into narrative later.

### Required Data Pulls

1. **Revenue & Forecast**
   - `unified_forecast_summary` — pipeline coverage, quota tracking, revenue at risk, team metrics
     - Current period: `period_offset: 0`
     - Previous period (for comparison): `period_offset: -1`
     - Also returns: `team_summary.revenue_per_rep` (period-scoped closed won ÷ quota-carrying reps — a productivity metric, distinct from quota attainment), `kpis.win_rate.by_deal_size` and `kpis.pipeline_coverage.by_deal_size` (org-adaptive deal-size bands), and `kpis.pipeline_coverage.acv_drift` (`drift_pct`, `direction`, `current_avg`, `historical_avg`, `is_significant` — drift >15%). `acv_drift` is always an object; treat it as a flag only when `is_significant: true`.
   - `forecast_confidence` — confidence scores, rep performance, velocity, stage distributions
   - `hunter_farmer_mix` (optional) — rep-level deal mix (net-new "hunting" vs expansion "farming"), for the optional rep deal-mix view on the Revenue Performance slide. Requires VIEW_TEAM_METRICS or team/all-metrics access — if unauthorized or empty, skip this pull and omit the corresponding slide element.

2. **ARR Growth**
   - `arr_growth_analytics` — total ARR, net retention, growth stage, benchmarks
     - Set `include_trends: true`, `include_changes: true`, `include_benchmarks: true`
     - Also returns: `grr` (Gross Revenue Retention — `renewal_arr / (renewal_arr + churned_arr)`, capped at 100%, excludes expansion), `logo_churn` (`rate`, `churned_logos`, `total_renewal_logos`), and `time_to_value` (`median_days`, `p75_days`, `contracts_measured` — contract start to first realized impact)
   - `arr_growth_narrative` — AI-generated growth narrative with recommendations (reasons about GRR, churn, and onboarding velocity)
   - `renewal_forecast_summary` — ARR renewing in 30/60/90/180-day windows, at-risk causes, and commit/best-case bands, for the forward-looking renewal risk block on the ARR Growth & Retention slide. Requires VIEW_TEAM_METRICS or team/all-metrics access — if unauthorized or empty, skip this pull and omit the block.

3. **Account Intelligence**
   - `account_intelligence_summary` — health scores, risk accounts, expansion candidates
   - `account_health_movement` — current vs prior snapshot health deltas (which accounts trended better/worse this quarter), for the health trend view on the Account Portfolio Review slide. Movement is correlational — accounts "trended down" or "moved to at-risk," never "caused" by a specific factor.

4. **Pipeline Risk**
   - `pipeline_risk_summary` — risk distribution, velocity issues, confidence metrics
   - `risk_heatmap` — deal-level risk with scores and risk factors (page 1, 25 results, sorted by risk score desc)
   - `deal_drag_dashboard` — stalled deals with waste scores and recovery strategies (sort_by="waste_score", page_size=5)

5. **Engagement**
   - `activity_gaps` — dormant accounts (default 30 days, limit 25)
   - `deal_drag_summary` — stalled deal count, avg waste score, total pipeline value stalled, risk distribution. This is the efficiency metric: "how much pipeline has stopped moving?"

6. **Process Diagnosis** (optional, manager/team-permission gated)
   - `revenue_loop_diagnosis` — the first failing Figure-Eight stage across the funnel; a process-level lens distinct from deal-level risk. Requires VIEW_TEAM_METRICS or team/all-metrics access — if unauthorized or empty, skip this pull and omit the corresponding slide.

7. **Deal Deep-Dives** (for win/loss narratives and context)
   - `get_opportunity` — retrieve full details for top 3 closed-won and top 2 closed-lost deals from the forecast summary
   - `get_opportunity_notes_summary` — AI-generated context for those same top wins and losses
   - `opportunity_framework_summary` — MEDDPIC/BANT/SPICED qualification context for those same top wins and losses (and optionally the top risk deals from `risk_heatmap`), to explain deals in qualification-framework terms rather than a risk number alone.

8. **Team Performance & Execution**
   - `team_action_plan` — rep completion rates, accountability data, high-priority items (limit 25)

9. **Post-Sale Health** (optional, board-level QBRs only)
   - `get_value_impact_card` — for top 3 accounts by ARR: fulfilment score, expansion readiness, impact evidence count

10. **Action Plan**
    - `weekly_action_plan` — prioritized next steps (limit 10)

### Handling Missing Data

Some tools may return sparse data or errors. Don't fail — adapt:
- If a tool returns no data, note it as "Data not available" in the relevant section and move on.
- If ARR growth has no trends, skip the trend chart and use the snapshot numbers.
- If risk heatmap is empty, note "No deals currently flagged as high risk" (which is a positive signal).
- `renewal_forecast_summary`, `revenue_loop_diagnosis`, and `hunter_farmer_mix` are manager/team-permission gated (require VIEW_TEAM_METRICS or team/all-metrics access). If any of these calls is unauthorized or returns empty, skip that block or slide gracefully — never fail the deck.
- `account_health_movement` reflects correlation, not causation. Slide and document copy must describe accounts as having "trended down" or "moved to at-risk" — never say an account's movement was "caused" by a specific factor.

## Step 3: Synthesize the Narrative

This is what separates a good QBR from a data dump. Before building slides, write a brief internal narrative outline:

1. **Headline**: One sentence capturing the quarter's story. Is it a growth story? A recovery story? A risk story? Examples:
   - "Strong quarter: 112% quota attainment driven by enterprise expansion"
   - "Pipeline coverage gap emerging: 1.8x vs 3x target needs attention"
   - "Retention held steady at 108% NRR despite two key churns"

2. **Three key themes**: What are the 3 things the audience should walk away remembering?

3. **One honest risk**: What's the biggest thing that could derail next quarter?

4. **One clear action**: What's the single most important thing to do next?

## Step 4: Build the Deck

Read the pptx skill's `pptxgenjs.md` reference for the technical details of creating slides. The deck structure below is your blueprint.

### Design System

Use the **Midnight Executive** palette for a premium, boardroom feel:

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

**Typography**: Georgia headers (36-44pt), Calibri body (14-16pt).

**Layout**: 16:9 widescreen. 0.5" margins minimum. Dark title/close slides, light content slides.

### Slide Structure

Build these slides in order. Each slide description includes what data to use and how to lay it out.

---

#### Slide 1: Title Slide
- **Background**: Navy (`1E2761`)
- **Content**: Company name, "Quarterly Business Review", quarter label (e.g., "Q1 2026"), date
- **Layout**: Centered, clean, minimal. Large Georgia title, smaller Calibri subtitle.

---

#### Slide 2: Executive Summary
- **Background**: Navy (`1E2761`)
- **Data source**: Your synthesized headline + three key themes from Step 3
- **Layout**: Large headline text (28-32pt, white), then 3 key takeaway bullets below (18pt, ice blue)
- This is the most important slide — it frames the entire review.

---

#### Slide 3: Revenue Performance
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `unified_forecast_summary` (both periods), `forecast_confidence`
- **Layout**: 3-4 large stat callouts across the top (quota attainment %, closed revenue, pipeline value, win rate). Below: bar chart comparing current vs previous quarter revenue. Use emerald for positive deltas, red for negative.
- **Key numbers to show**: Quota attainment %, total closed revenue, comparison to previous quarter, pipeline coverage ratio.
- **Productivity & segmentation**: Add **Revenue per Rep** (`team_summary.revenue_per_rep`) as a stat callout — it shows per-head productivity, which quota attainment alone hides. If `kpis.win_rate.by_deal_size` shows a meaningful spread across bands, add a small horizontal bar set "Win Rate by Deal Size" — a healthy blended win rate often masks a weak segment, and the QBR is the right venue to expose it.
- **Rep deal-mix (optional)**: If `hunter_farmer_mix` is available (requires VIEW_TEAM_METRICS or team/all-metrics access), add a small stacked-bar or split-stat next to Revenue per Rep showing each rep's mix of net-new "hunting" vs expansion "farming" deals — it explains *how* revenue per rep was earned, not just how much. If the call is unauthorized or returns empty, omit this element and keep the slide as-is.

---

#### Slide 4: ARR Growth & Retention
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `arr_growth_analytics`, `arr_growth_narrative`
- **Layout**: Left side — large ARR number with growth % delta, NRR percentage, growth stage label. Right side — line chart of ARR trend if trend data is available, or a stat card layout if not.
- **Retention block**: This slide is now the retention story, not just growth. Show **NRR and GRR as a pair** — NRR is the expansion-inclusive number, GRR is gross retention (capped at 100%, color-coded green ≥90% / amber ≥80% / red <80%). Add **Logo Churn** (`rate` plus `churned_logos`/`total_renewal_logos`) as a count-based companion to GRR's dollar-based view. Add **Time-to-Value** (`median_days`, with `p75_days` and `contracts_measured`) as an onboarding-velocity stat — it connects sales execution to realized customer value.
- **Include**: Benchmark comparison (how does NRR compare to best-in-class?). If NRR and GRR diverge sharply, state plainly that expansion is offsetting churn.
- Pull key quotes/insights from the narrative tool to add a 1-2 sentence insight below the numbers.
- **Renewal risk (forward-looking)**: The blocks above are backward-looking (retention history). If `renewal_forecast_summary` is available (requires VIEW_TEAM_METRICS or team/all-metrics access), add a "Renewals Coming Due" block showing ARR renewing in 30-180 days, broken out by window, with at-risk causes called out and commit vs best-case bands shown side by side. This turns the retention story forward — not just "how we did" but "what's coming." If the call is unauthorized or returns empty, omit this block and keep the slide retention-history-only.

---

#### Slide 5: Pipeline Health
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `unified_forecast_summary`, `forecast_confidence`
- **Layout**: Pipeline coverage ratio as a large callout. Below: horizontal stacked bar or pie chart showing stage distribution. Add velocity metrics (avg days in stage, deal cycle time) if available.
- **Key metrics**: Coverage ratio vs target (3x is standard), stage distribution, pipeline velocity, new pipeline created this quarter.
- **Pipeline composition**: Add a "Pipeline by Deal Size" mini-chart from `kpis.pipeline_coverage.by_deal_size` (% of pipeline value per band) — coverage in aggregate can look healthy while being concentrated in one band. If `kpis.pipeline_coverage.acv_drift.is_significant` is `true`, add an amber callout: "Pipeline ACV is {direction} {drift_pct}% vs trailing-12-month closed-won average — current deals are {larger/smaller} than what the team has historically converted, which puts forecast confidence at risk." If `is_significant` is `false`, omit the callout (do not surface non-significant drift as a risk).

---

#### Slide 6: Risk & Concentration Analysis
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `pipeline_risk_summary`, `risk_heatmap`, `deal_drag_summary`, `deal_drag_dashboard`
- **Layout**: Top row — risk distribution summary (high/medium/low counts) as colored stat cards. Add a "Stalled Pipeline" stat card showing total $ value of stalled deals from `deal_drag_summary` (red if stalled value > 10% of total pipeline). Below: table of top 5-8 highest-risk deals from the heatmap with deal name, amount, `healthScore`, server-supplied `healthBand`, and top risk factor. Order by `healthScore` ascending and color `Low` red, `Medium` amber, `High` emerald.
- If stalled deals exist, add a brief callout below the table: "X deals ($Y) have been stalled for 30+ days — recommended action: immediate executive review."
- Use red/amber/emerald color coding for risk levels.
- **Qualification context**: For each deal in the top-risk table, add a short qualification note from `opportunity_framework_summary` — the deal's MEDDPIC, BANT, or SPICED gaps (whichever framework the org uses), so the risk score is explained in qualification terms (e.g., "Economic Buyer unconfirmed," "no compelling event identified") rather than left as a bare number.

**Subsection: Recovery Actions** — Extract top 3 stalled deals from `deal_drag_dashboard` and show deal name, waste score, and the specific recovery_strategy from the API response. Keep this brief (3 rows max). Frame as "Recommended Recovery Strategies" to emphasize proactive action.

---

#### Slide 7: Account Portfolio Review
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `account_intelligence_summary`, `account_health_movement`
- **Layout**: Health score distribution (healthy/at-risk/critical counts). Two-column layout below: left column lists top expansion candidates with ARR and expansion signal, right column lists at-risk accounts with health score and risk reason.
- Cap each list at 5 accounts to keep the slide readable.
- **Health trend (movement)**: Add a "Health Trend" block comparing the current snapshot to the prior period using `account_health_movement` — call out which accounts moved *worse* this quarter (e.g., healthy → at-risk, at-risk → critical) as a short list with account name, prior score, current score, and delta. Movement is correlational: describe accounts as having "trended down" or "moved to at-risk," never "caused" by a specific factor. If the tool returns no prior-snapshot data, omit this block and keep the static distribution only.

---

#### Slide 8: Engagement & Activity Gaps
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `activity_gaps`
- **Layout**: Count of dormant accounts as a large warning callout. Below: table of top 10 dormant accounts with account name, days since last activity, and ARR at risk.
- This slide is a call to action — frame dormant accounts as revenue at risk.

---

#### Slide 9: Key Wins & Losses
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `get_opportunity` and `get_opportunity_notes_summary` for top 3 closed-won and top 2 closed-lost deals (pulled in Step 2)
- **Layout**: Two-column. Left: "Wins" with emerald accent. Right: "Losses" with red accent. For each deal, construct a 1-2 sentence narrative using: deal name, amount, key stage progression, and thematic insight from the notes summary.
  - Example win: "Acme Enterprise ($250K) — expanded from platform to enterprise tier after demonstrating ROI in Q3, closed following expanded C-suite alignment."
  - Example loss: "TechCorp ($85K) — stalled in negotiation due to budget reallocation; prospect indicated interest for Q3 2026."
- If specific deal data isn't available, fall back to: note "Connect your CRM for deal-level win/loss tracking" and skip to next slide.
- **Qualification context**: Pull `opportunity_framework_summary` for the same top wins and losses and add one qualification-framework note per deal — MEDDPIC, BANT, or SPICED, whichever the org uses — e.g., "Economic Buyer confirmed pre-close" for a win or "no compelling event, Budget unconfirmed" for a loss. This explains deals in qualification terms, not just outcome facts.

---

#### Slide 10: Next Quarter Plan & Actions
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `team_action_plan` (current period completion rates), `weekly_action_plan`, your synthesized narrative from Step 3
- **Layout**: Add a "Team Execution Baseline" stat card at the top showing average team action completion rate from the current quarter (e.g., "Team averaged 78% action completion this quarter"). Below: numbered list of top 5-7 prioritized actions. Each action should have: what to do, why it matters, and the expected impact. Use icon-style bullets (numbered circles in emerald).

---

#### Slide 11: Value & Expansion Health (Optional — Board-Level QBRs Only)
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `get_value_impact_card` for top 3 accounts by ARR
- **When to include**: Only when audience is board/executive level. Omit for sales leadership QBRs.
- **Layout**: Three-column card layout. For each top account: show account name, fulfilment score, expansion readiness category (e.g., "Ready to Expand", "At Risk", "Stable"), and key impact evidence count. Use color coding (emerald for "Ready to Expand", amber for "Stable", red for "At Risk").
- **Narrative**: Add a 1-2 sentence summary below: "Top 3 accounts show strong fulfilment (avg X score) with Y expansion opportunities identified. Focus on [category] for Q2 growth."

---

#### Slide 12: Where Deals Break Down (Optional — Conditional on Data Availability)
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `revenue_loop_diagnosis`
- **When to include**: Only when the tool is available and authorized (requires VIEW_TEAM_METRICS or team/all-metrics access) and returns data. If the call is unauthorized or empty, skip this slide entirely — do not fail the deck.
- **Layout**: Show the Figure-Eight funnel as a horizontal stage flow, highlighting the first failing stage with a red marker. Below, a short stat callout with the stage name, the drop-off severity, and a 1-2 sentence diagnosis.
- **Framing**: This is a process-level lens, distinct from deal-level risk (Slide 6) — it answers "where does the team's revenue process itself break down?" rather than "which deals are at risk?" Frame it as a systemic/process insight, not a rep-performance callout.

---

#### Slide 13: Closing Slide
- **Background**: Navy (`1E2761`)
- **Content**: "Thank You" or "Questions?", company name, date
- **Layout**: Clean, centered, minimal. Mirror the title slide design.

---

### Chart Generation

For charts embedded in slides, generate them as PNG images using a Node.js script with a charting library, then embed them in the PPTX. Alternatively, use PptxGenJS's built-in chart support (bar, line, pie) which renders natively in PowerPoint.

Prefer native PptxGenJS charts when possible — they're editable in PowerPoint and look sharper. Use the chart styling guidance from pptxgenjs.md (custom colors matching the palette, clean backgrounds, muted axis labels, subtle grid lines).

## Step 5: Generate the File

Use the pptx skill's approach:

1. Write a Node.js script using PptxGenJS that constructs all slides
2. Embed the data directly in the script (no external data files needed)
3. Run the script to generate the .pptx file
4. Save to the outputs folder

If the user requested DOCX format instead, read the docx skill's SKILL.md and follow its patterns. Structure the document with the same sections as the deck, using proper heading hierarchy, tables for data, and narrative paragraphs between sections.

## Step 6: QA

After generating the file:

1. Convert to images using the pptx skill's conversion approach
2. Visually inspect every slide — check for overlapping text, missing data, color contrast issues
3. Verify all data points match what was pulled from the MCP tools
4. Fix any issues and re-verify

## DOCX Alternative

If the user requests a document instead of a deck, structure it as:

```
QUARTERLY BUSINESS REVIEW — [Quarter] [Year]

1. Executive Summary
   [Narrative paragraph with headline and key themes]

2. Revenue Performance
   [Table: Metric | This Quarter | Last Quarter | Delta]
   [Optional: Rep deal-mix — net-new hunting vs expansion farming, from hunter_farmer_mix]
   [Narrative: what drove the numbers]

3. ARR Growth & Retention
   [Table: Metric | Value | Benchmark — rows: ARR, ARR Growth %, NRR, GRR, Logo Churn, Time-to-Value (median days), Revenue per Rep]
   [Table: Renewals Coming Due — Window (30/60/90/180 days) | ARR Renewing | At-Risk Causes | Commit | Best Case, from renewal_forecast_summary; omit if unauthorized or empty]
   [Narrative: growth stage, durability of retention, onboarding velocity — pull from arr_growth_narrative]

4. Pipeline Health
   [Table: Stage | Count | Value | Avg Days]
   [Pipeline mix by deal size; ACV drift note only if significant]
   [Narrative: coverage, velocity, concerns]

5. Risk Analysis
   [Table: Deal | Amount | Risk Score | Top Risk Factor | Qualification Note (MEDDPIC/BANT/SPICED, from opportunity_framework_summary)]
   [Narrative: concentration risk, mitigation actions]

6. Where Deals Break Down (Optional — Conditional on Data Availability)
   [First failing Figure-Eight stage, drop-off severity, 1-2 sentence diagnosis, from revenue_loop_diagnosis]
   [Omit entirely if the tool is unauthorized or returns no data. Frame as process-level, distinct from Section 5's deal-level risk.]

7. Account Portfolio
   [Table: Account | Health | ARR | Signal]
   [Table: Health Trend — Account | Prior Score | Current Score | Delta, from account_health_movement; describe as "trended down"/"moved to at-risk," never "caused"]
   [Narrative: expansion opportunities, churn risks]

8. Engagement Gaps
   [Table: Account | Days Dormant | ARR at Risk]

9. Key Wins & Losses
   [Two tables with narrative]
   [Qualification-framework note per deal, from opportunity_framework_summary]

10. Next Quarter Plan
   [Numbered action items with owners and deadlines]
```

## Tips for Great QBRs

- **Lead with insight, not data.** Every slide should answer "so what?" before showing numbers.
- **Use comparisons.** Raw numbers are meaningless without context — show quarter-over-quarter deltas, benchmark comparisons, and target vs actual.
- **Be honest about risk.** The credibility of your QBR depends on acknowledging what's not going well.
- **End with clear actions.** The audience should leave knowing exactly what happens next.
