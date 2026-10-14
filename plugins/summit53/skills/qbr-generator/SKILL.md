---
name: "qbr-generator"
description: "Build an internal quarterly revenue and sales operating review as an executive PPTX from live Summit53 data: quota and revenue performance, ARR growth and retention, pipeline health, risk and stalled pipeline, account portfolio, wins and losses, and next-quarter actions. DOCX only when explicitly requested. Use when a revenue or sales leader says 'prep for my QBR', 'build my quarterly deck', 'quarterly business review', 'quarterly sales review', 'executive revenue review', 'pull together the numbers for this quarter', 'I need a revenue review', or wants the quarter's CRM performance compiled into an internal presentation. Despite the name, do not use for a customer-facing QBR or value review — use customer-qbr. Do not use for board or investor reporting — use board-revenue-pack. Do not use for the weekly 'why did the number move' brief — use forecast-delta-brief."
metadata:
  version: "1.3.0"
  baselined: "2026-10-13"
  status: "active"
---

# QBR Generator

Turn live Summit53 revenue evidence into an internal quarterly operating review: one headline narrative, the honest risks, quarter-over-quarter movement, and the few forward decisions that matter. The default deliverable is a PPTX deck; a DOCX is produced only when the user explicitly asks for one.

## Route first

- Use this skill for an **internal** quarterly revenue or sales operating review for leadership.
- Customer-facing QBR, value review or success review for a named customer → `customer-qbr`. Never present this internal deck to a customer.
- Board, investor or fundraise revenue pack → `board-revenue-pack`. Do not blend board framing into an internal operating QBR.
- Weekly "why did the forecast move" brief → `forecast-delta-brief`.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its checklist before any data call. It covers tenant resolution (`current_context` first), picking between multiple Summit53 connectors, loading deferred tools in one batch ([host-adapters.md](references/host-adapters.md#loading-the-summit53-tools)), live-schema discovery, read-only discipline (never `refresh: true`), fixture exclusion, unavailable-is-not-zero, correlational language and one-link delivery.

Read [references/async-envelopes.md](references/async-envelopes.md) before the first `unified_forecast_summary` call: it defines how to poll processing envelopes with `get_job` and re-call for the payload.

Read [references/currency-and-fx.md](references/currency-and-fx.md) before writing any amount on a slide: it defines reporting-currency labels, disclosure of excluded or unconverted amounts, constant currency and FX effect. Its checklist is part of this skill's final verification.

Read [references/host-adapters.md](references/host-adapters.md) for how this host loads tools, builds and renders the deck, builds any DOCX, and saves and delivers files.

Skill-specific gates (resolve these up front — see Step 1):

1. **Reporting period, comparison period, currency and audience are resolved before data is pulled**, from the request or context, and every assumption is stated on the Executive Summary slide and in the delivery note.
2. **Scope.** Org-wide unless the user names a team, segment or region; every returned organization ID must match `scoped_org_id`.
3. **One currency.** Use the reporting currency the tools return (`metadata.currency`, or a top-level `currency` where a tool returns one — never assume USD). Never add or compare amounts across currencies; if a payload mixes currencies without a converted total, show the native figures separately and say so. Never convert an amount yourself.
4. **Demo label.** This is a commercial artifact. If fixture rows cannot be separated from real records, put **Demo data — not for customer or commercial decisions** on the title slide and in the footer of every slide. A tenant whose `current_context` reports `organization.is_demo: true` is always a demo run, in every environment: apply the label and follow [Demo tenants](references/connector-preflight.md#demo-tenants).

## Why This Exists

Every revenue leader does QBRs, and building them is painful — hours of pulling data from dashboards, formatting slides, writing narratives. This skill does it in one shot: live CRM data flows into a professional, story-driven deliverable.

## Tools Reference

This skill uses the following Summit53 tools (logical names; resolve the prefix per the preflight, and inspect each live schema before the first call — argument names below are semantic guidance):

**Gate & discovery**: `current_context` (always first), `list_available_tools` (confirms which optional, permission-gated tools are exposed)

**Revenue & Forecast**: `unified_forecast_summary` (incl. revenue per rep, win rate & coverage by deal size, ACV drift), `get_job`, `forecast_confidence`, `hunter_farmer_mix` (optional, manager/team-permission gated — rep deal-mix: net-new hunting vs expansion farming)

> **Async contract:** each `unified_forecast_summary` period can return a processing envelope. Follow [references/async-envelopes.md](references/async-envelopes.md): poll that call's `job_id` with `get_job` until terminal, then re-call the original tool with identical arguments for the payload. Current and prior periods are separate jobs. Never render a processing envelope as blank or zero data.

**ARR Growth**: `arr_growth_analytics` (incl. GRR, logo churn, time-to-value), `arr_growth_narrative`, `renewal_forecast_summary` (manager/team-permission gated — forward-looking renewal risk: ARR renewing in 30-180 days, at-risk causes, commit/best-case bands)

**Account Intelligence**: `account_intelligence_summary`, `account_health_movement` (current vs prior snapshot — correlational health trend, not a static snapshot)

**Pipeline Risk & Efficiency**: `pipeline_risk_summary`, `risk_heatmap`, `deal_drag_summary`, `deal_drag_dashboard`, `revenue_loop_diagnosis` (optional, manager/team-permission gated — first failing Figure-Eight stage, a process-level lens)

**Engagement**: `activity_gaps`

**Deal Deep-Dives**: `get_opportunity`, `get_opportunity_notes_summary`, `opportunity_framework_summary` (MEDDPIC/BANT/SPICED qualification context)

**Team Performance**: `team_action_plan`

**Regional view (optional)**: `arr_operating_summary` (read `by_dimension.dimension_options` only, to learn whether `sales_region` / `market_region` are available), `segment_performance_summary` (`dimension`, `level="top"`, optional `secondary` cross-tab; requires analytics permission)

**Post-Sale Health**: `get_value_impact_card` (optional)

**Action Planning**: `weekly_action_plan`

## Step 1: Clarify Scope

Resolve these **before** pulling data — from the request or available context where possible; ask only for what you cannot infer. If the user says "just do it", apply the defaults and state each one as an assumption.

- **Reporting period**: Which quarter? Default to the current quarter as the forecast tool defines it (`period_offset: 0`). Once the first payload returns, record the actual start/end dates and whether the period is fiscal or calendar, and use those dates on the title slide.
- **Comparison period**: Default to the previous quarter (`period_offset: -1`). If the user wants year-over-year or another baseline, confirm the tools can return it; if not, say so rather than substituting a different baseline silently.
- **Currency**: The reporting currency the tools return. Confirm it from the first payload and state it on the title slide.
- **Audience**: Executive leadership (high-level narrative — the default) or sales leadership (operational detail). Board or investor audiences route to `board-revenue-pack`; customer audiences route to `customer-qbr`.
- **Team scope and focus areas**: Org-wide by default; any team, segment, accounts or reps to highlight?
- **Format**: PPTX. Produce a DOCX only if the user explicitly asks for one (see DOCX Companion below) — do not offer it as a default choice.

## Step 2: Pull All Data

Call these Summit53 tools. Launch as many in parallel as possible — they're independent. Capture the raw responses, including every denominator, sample size, as-of timestamp and data-quality flag they carry; you'll synthesize them into narrative later and those caveats must survive into the deck.

### Required Data Pulls

1. **Revenue & Forecast**
   - `unified_forecast_summary` — pipeline coverage, quota tracking, revenue at risk, team metrics
     - Current period: `period_offset: 0`
     - Previous period (for comparison): `period_offset: -1`
     - Also returns `projected_landing` `{value, basis, closed_won, floored_to_closed_won, fallback_reason, rep_commit, weighted_pipeline, window}` — the landing number leads with the reps' commit roll-up (`basis: "rep_commit_rollup"`) and falls back to weighted pipeline (`basis: "weighted_pipeline"`) with a `fallback_reason`. Capture all of it for Slide 3.
     - Quota rollups carry `constant_currency` `{label, attainment_percentage, fx_effect_pts, spans_fiscal_years, …}` — attainment restated at plan rates. Capture it for Slide 3.
     - Also returns: `team_summary.revenue_per_rep` (period-scoped closed won ÷ quota-carrying reps — a productivity metric, distinct from quota attainment), `kpis.win_rate.by_deal_size` and `kpis.pipeline_coverage.by_deal_size` (org-adaptive deal-size bands), and `kpis.pipeline_coverage.acv_drift` (`drift_pct`, `direction`, `current_avg`, `historical_avg`, `is_significant` — drift >15%). `acv_drift` is always an object; treat it as a flag only when `is_significant: true`.
   - `forecast_confidence` — confidence scores, rep performance, velocity, stage distributions
   - `hunter_farmer_mix` (optional) — rep-level deal mix (net-new "hunting" vs expansion "farming"), for the optional rep deal-mix view on the Revenue Performance slide. Requires VIEW_TEAM_METRICS or team/all-metrics access — if unauthorized or empty, skip this pull and omit the corresponding slide element.

2. **ARR Growth**
   - `arr_growth_analytics` — total ARR, net retention, growth stage, benchmarks
     - Set `include_trends: true`, `include_changes: true`, `include_benchmarks: true`
     - `include_changes` also returns `constant_currency` `{label, current, previous, delta, actual_delta, fx_effect, excluded_currencies, status, footnote}`; `include_trends` returns `trends.constant_currency`. `delta` is constant-currency change, `actual_delta` the reported change, `fx_effect` the difference.
     - Also returns: `grr` (Gross Revenue Retention — `renewal_arr / (renewal_arr + churned_arr)`, capped at 100%, excludes expansion), `logo_churn` (`rate`, `churned_logos`, `total_renewal_logos`), and `time_to_value` (`median_days`, `p75_days`, `contracts_measured` — contract start to first realized impact)
   - `arr_growth_narrative` — AI-generated growth narrative with recommendations (reasons about GRR, churn, and onboarding velocity)
   - `renewal_forecast_summary` — ARR renewing in 30/60/90/180-day windows, at-risk causes, and commit/best-case bands, for the forward-looking renewal risk block on the ARR Growth & Retention slide. Requires VIEW_TEAM_METRICS or team/all-metrics access — if unauthorized or empty, skip this pull and omit the block.

3. **Account Intelligence**
   - `account_intelligence_summary` — health scores, risk accounts, expansion candidates
   - `account_health_movement` — current vs prior snapshot health deltas (which accounts trended better/worse this quarter), for the health trend view on the Account Portfolio Review slide. Movement is correlational — accounts "trended down" or "moved to at-risk," never "caused" by a specific factor.

4. **Pipeline Risk**
   - `pipeline_risk_summary` — risk distribution, velocity issues, confidence metrics
   - `risk_heatmap` — deal-level risk with scores and risk factors (page 1, 25 results). Treat `score_semantics` as authoritative: higher `healthScore` is healthier, `riskScore` is only a deprecated alias. Sort for the riskiest deals by `healthScore` ascending, never by `riskScore` descending
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

9. **Post-Sale Health** (optional, executive-audience QBRs only)
   - `get_value_impact_card` — for top 3 accounts by ARR: fulfilment score, expansion readiness, impact evidence count

10. **Action Plan**
    - `weekly_action_plan` — prioritized next steps (limit 10)

11. **Regional Performance** (optional)
    - `arr_operating_summary` — read `by_dimension.dimension_options`. Proceed only for a dimension whose `available` is true (`sales_region` = Sales Org team tree, `market_region` = geographic market tree).
    - `segment_performance_summary` with `dimension` set to the available region dimension, `level: "top"`, and the same period as the forecast pull. Returns `groups[]`, `unassigned`, `tree[]`, `strongest_groups` / `weakest_groups` and `dimension_source`.
    - If both region dimensions are available and the audience is sales leadership, optionally add `secondary` (e.g. `dimension: "sales_region"`, `secondary: "market_region"`) for the `crosstab` — `home_markets` and `cross_market` show which teams sell outside their home market.
    - `data_quality_score` (optional) — `issues.accounts_missing_country` and deal-currency-without-rate counts are the coverage caveat for any regional view.
    - Unavailable dimension, access denial or an empty result → omit the regional slide and list it on Sources & Limits.

### Handling Missing Data

Some tools may return sparse data or errors. Don't fail — adapt. Missing data is **never zero and never a positive signal**:
- If a tool returns no data, mark the metric "unavailable" with a one-line reason in the relevant section and on the Sources & Limits slide, and move on. Never render it as `0`, a dash, or a green status.
- If ARR growth has no trends, skip the trend chart and use the snapshot numbers.
- If `risk_heatmap` is empty, that is **indeterminate**, not healthy — note "Deal-level risk unavailable for this period" unless the payload explicitly confirms zero deals in scope.
- If `activity_gaps` returns nothing, say "Dormancy data unavailable", not "no dormant accounts".
- `renewal_forecast_summary`, `revenue_loop_diagnosis`, and `hunter_farmer_mix` are manager/team-permission gated (require VIEW_TEAM_METRICS or team/all-metrics access). If any of these calls is unauthorized or returns empty, skip that block or slide gracefully — never fail the deck, and never show the permission error on a slide. List the omitted metric on the Sources & Limits slide as "not included (access-gated)".
- `account_health_movement` reflects correlation, not causation. Slide and document copy must describe accounts as having "trended down" or "moved to at-risk" — never say an account's movement was "caused" by a specific factor.

## Step 3: Synthesize the Narrative

This is what separates a good QBR from a data dump. Before building slides, reconcile the figures once (the same numbers feed every slide and any DOCX), then write a brief internal narrative outline:

1. **Headline**: One sentence capturing the quarter's story. Is it a growth story? A recovery story? A risk story? Examples:
   - "Strong quarter: 112% quota attainment, with enterprise expansion the largest contributor"
   - "Pipeline coverage gap emerging: 1.8x vs 3x target needs attention"
   - "Retention held steady at 108% NRR alongside two key churns"

   Describe health movement, interventions and execution signals as correlational ("moved alongside", "coincided with") unless a source proves causation.

2. **Three key themes**: What are the 3 things the audience should walk away remembering?

3. **One honest risk**: What's the biggest thing that could derail next quarter? Weak metrics stay in the deck — do not drop or soften a bad number to protect the headline.

4. **One clear action**: What's the single most important thing to do next?

## Step 4: Build the Deck

Build with the host's presentation toolchain: load it per [host-adapters.md](references/host-adapters.md#building-slides) before writing any code. The deck structure below is your blueprint — favor a coherent executive story over exhaustive dashboard coverage, and drop a slide whose sources were all unavailable rather than rendering an empty frame.

**Preserve the evidence on the slide.** Show denominators and sample sizes next to rates (win rate "(n = 42 closed)", logo churn "3 of 57 renewal logos", time-to-value "median 41 days, 18 contracts measured", revenue per rep "across 9 quota-carrying reps"), the as-of timestamp of each source in the slide footer, and any data-quality caveat the tool returned. A rate without its denominator is not shippable.

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
- **Content**: Company name, "Quarterly Business Review — Internal", quarter label with its actual date range (e.g., "Q1 FY2026 · 1 Jan – 31 Mar 2026"), reporting currency, date prepared
- **Layout**: Centered, clean, minimal. Large Georgia title, smaller Calibri subtitle.

---

#### Slide 2: Executive Summary
- **Background**: Navy (`1E2761`)
- **Data source**: Your synthesized headline + three key themes from Step 3
- **Layout**: Large headline text (28-32pt, white), then 3 key takeaway bullets below (18pt, ice blue). A small assumptions line at the bottom (12pt): reporting period, comparison period, currency, scope, and any default you applied.
- This is the most important slide — it frames the entire review.

---

#### Slide 3: Revenue Performance
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `unified_forecast_summary` (both periods), `forecast_confidence`
- **Layout**: 3-4 large stat callouts across the top (quota attainment %, closed revenue, pipeline value, win rate). Below: bar chart comparing current vs previous quarter revenue. Use emerald for positive deltas, red for negative.
- **Key numbers to show**: Quota attainment %, total closed revenue, comparison to previous quarter, pipeline coverage ratio.
- **Projected landing**: Show `projected_landing.value` as the forecast landing callout with its basis in plain words — "reps' commit roll-up" or "weighted pipeline (fallback: {fallback_reason})". If `floored_to_closed_won` is true, say the landing was floored at closed-won. Never present the landing without its basis.
- **Constant-currency attainment**: When the quota `constant_currency` block is present and `fx_effect_pts` is material, show reported and constant-currency attainment side by side, labelled with the block's `label` (e.g. "FY2027 plan rates"), and name `fx_effect_pts` as currency, not performance. Omit for single-currency organizations. Note `spans_fiscal_years` when true.
- **Productivity & segmentation**: Add **Revenue per Rep** (`team_summary.revenue_per_rep`) as a stat callout — it shows per-head productivity, which quota attainment alone hides. If `kpis.win_rate.by_deal_size` shows a meaningful spread across bands, add a small horizontal bar set "Win Rate by Deal Size" — a healthy blended win rate often masks a weak segment, and the QBR is the right venue to expose it.
- **Rep deal-mix (optional, sales-leadership audience only)**: If `hunter_farmer_mix` is available (requires VIEW_TEAM_METRICS or team/all-metrics access), add a small stacked-bar or split-stat next to Revenue per Rep showing each rep's mix of net-new "hunting" vs expansion "farming" deals — it explains *how* revenue per rep was earned, not just how much. If the call is unauthorized or returns empty, omit this element and keep the slide as-is.

---

#### Slide 4: ARR Growth & Retention
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `arr_growth_analytics`, `arr_growth_narrative`
- **Layout**: Left side — large ARR number with growth % delta, NRR percentage, growth stage label.
- **Reported vs constant currency**: Read `constant_currency.status`. `single_currency` → no FX discussion. Otherwise, when `fx_effect` is material (more than about 2% of the reported change, or it flips the sign), show reported growth (`actual_delta`) and constant-currency growth (`delta`) side by side, with the FX effect as its own line, labelled with `label`; a `partial` status carries its `footnote` and `excluded_currencies`. FX effect is never churn, contraction or expansion. No `constant_currency` block → "constant currency unavailable (plan rates not configured)". The trend chart may add the `trends.constant_currency` series. Right side — line chart of ARR trend if trend data is available, or a stat card layout if not.
- **Retention block**: This slide is now the retention story, not just growth. Show **NRR and GRR as a pair** — NRR is the expansion-inclusive number, GRR is gross retention (capped at 100%, color-coded green ≥90% / amber ≥80% / red <80%). Add **Logo Churn** (`rate` plus `churned_logos`/`total_renewal_logos`) as a count-based companion to GRR's dollar-based view. Add **Time-to-Value** (`median_days`, with `p75_days` and `contracts_measured`) as an onboarding-velocity stat — it connects sales execution to realized customer value.
- **Include**: Benchmark comparison **only** when `arr_growth_analytics` returns benchmarks (`include_benchmarks: true`) — cite them as the tool's benchmark, with its basis. Never invent or recall a "best-in-class" figure from memory; if no benchmark is returned, omit the comparison. If NRR and GRR diverge sharply, state plainly that expansion is offsetting churn.
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

#### Slide 5b: Regional Performance (Optional — Conditional on Region Dimensions)
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `segment_performance_summary` (region dimension, `level: "top"`), optionally its `crosstab`; `data_quality_score` for coverage
- **When to include**: Only when `dimension_options` shows `sales_region` or `market_region` available and the call returns data. Otherwise skip the slide and list it on Sources & Limits.
- **Layout**: A table or horizontal bar set per top-level region: ARR, new ARR, win rate (with n), pipeline coverage — plus the **Unassigned** row, always shown (with `accounts_missing_market` where present). Mark `strongest_groups` / `weakest_groups` with emerald / amber. Name `dimension_source` in a one-line footnote.
- **Cross-tab (optional, sales-leadership audience)**: For `sales_region` × `market_region`, a compact matrix from `crosstab.cells` with row and column totals; flag `cross_market` cells as selling outside the home market and name the `home_markets.source` basis.
- **Guardrails**: Market rows may carry `tam` / `tam_currency` — never sum a parent TAM when any child TAM is missing. If a region trades in several currencies, `metrics.native_by_currency` can show the foreign share; never sum native amounts across currencies. Put `accounts_missing_country` and currency-without-rate counts in the footnote as coverage caveats. Region rows are team- and market-level; no per-rep ranking on an executive deck.

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
- **Layout**: Count of dormant accounts as a large warning callout, with the dormancy threshold used (e.g., "no logged activity in 30+ days"). Below: table of top 10 dormant accounts with account name, days since last logged activity, and ARR at risk.
- This slide is a call to action — frame dormant accounts as revenue at risk. "Dormant" means no logged CRM activity; it is not proof the customer is disengaged, so say "no logged activity", not "gone silent".

---

#### Slide 9: Key Wins & Losses
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `get_opportunity` and `get_opportunity_notes_summary` for top 3 closed-won and top 2 closed-lost deals (pulled in Step 2)
- **Layout**: Two-column. Left: "Wins" with emerald accent. Right: "Losses" with red accent. For each deal, construct a 1-2 sentence narrative using: deal name, amount, key stage progression, and thematic insight from the notes summary.
  - Example win: "Acme Enterprise (USD 250K) — expanded from platform to enterprise tier after demonstrating ROI in Q3, closed following expanded C-suite alignment."
  - Example loss: "TechCorp (USD 85K) — stalled in negotiation due to budget reallocation; prospect indicated interest for Q3 2026."
- If specific deal data isn't available, drop the slide and list "Deal-level win/loss detail: unavailable" on the Sources & Limits slide.
- Win and loss narratives come from the notes summary; write what happened alongside the outcome, not a causal verdict on why it was won or lost unless the notes record the buyer's stated reason.
- **Qualification context**: Pull `opportunity_framework_summary` for the same top wins and losses and add one qualification-framework note per deal — MEDDPIC, BANT, or SPICED, whichever the org uses — e.g., "Economic Buyer confirmed pre-close" for a win or "no compelling event, Budget unconfirmed" for a loss. This explains deals in qualification terms, not just outcome facts.

---

#### Slide 10: Next Quarter Plan & Actions
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `team_action_plan` (current period completion rates), `weekly_action_plan`, your synthesized narrative from Step 3
- **Layout**: Add a "Team Execution Baseline" stat card at the top showing average team action completion rate from the current quarter (e.g., "Team averaged 78% action completion this quarter", with the number of actions it is based on). Keep it team-level: no per-rep completion rankings on this slide. Below: numbered list of top 5-7 prioritized actions. Each action should have: what to do, why it matters, and the expected impact. Use icon-style bullets (numbered circles in emerald).

---

#### Slide 11: Value & Expansion Health (Optional — Executive-Audience QBRs Only)
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `get_value_impact_card` for top 3 accounts by ARR
- **When to include**: Only when the audience is executive leadership. Omit for sales-leadership QBRs. (Board audiences use `board-revenue-pack`.)
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

#### Slide 13: Sources & Limits
- **Background**: Off-white (`F8FAFC`)
- **Content**: a compact two-column list at 11-12pt.
  - **Sources**: each tool used, its as-of / generated timestamp, the reporting and comparison periods, the currency, and the rates basis (`rates_as_of`, plan-rate `label` where constant currency is shown).
  - **Currency exclusions**: when `normalization` is `converted_excluding_unconverted` or the `fx_unconverted_amounts_excluded` warning appears, list the excluded native amounts by currency from `unconverted_amounts` — and also note the exclusion beside the affected total on its own slide, not only here. If the excluded share could change a conclusion, call it provisional.
  - **Limits**: every metric that is unavailable, access-gated, stale, low-sample or carries a tool data-quality caveat, one plain line each ("Renewal forecast: not included (access-gated)", "Win rate by deal size: <10 closed deals per band"). No raw permission errors, stack traces or tool error text.
  - Excluded fixture rows, or the demo label if the preflight required one.

---

#### Slide 14: Closing Slide
- **Background**: Navy (`1E2761`)
- **Content**: "Thank You" or "Questions?", company name, date
- **Layout**: Clean, centered, minimal. Mirror the title slide design.

---

### Chart Generation

**Money formatting**: any `formatCurrency`-style helper in the deck script takes the reporting currency code from the response and renders the ISO code or its unambiguous symbol (`NZ$`, `A$`, `US$`, `€`, `£`) — never a hard-coded `$`. A bare `$` is acceptable only when the reporting currency is USD and the audience is US-only. Chart value-axis labels follow the same rule.

Use native charts (bar, line, pie, stacked bar); they're editable in PowerPoint and look sharper. Set titles and data labels, use palette colours, muted axis labels and subtle grid lines. When building with PptxGenJS (Claude's pptx skill), use `addChart()` and pass `chartColors` from the palette. Fall back to an image only for a chart type PowerPoint cannot draw natively.

## Step 5: Generate the File

Use the host's presentation toolchain ([host-adapters.md](references/host-adapters.md#building-slides)):

1. Write one generator that constructs all slides
2. Embed the reconciled data directly in the generator (no external data files needed)
3. When building with PptxGenJS (Claude's pptx skill), use factory functions for option objects (PptxGenJS mutates them — never reuse one across calls)
4. Run the generator to produce the .pptx file
5. Save as `QBR-[Quarter]-[Year].pptx` where the host keeps deliverables ([host-adapters.md](references/host-adapters.md#saving-and-delivering-files))

Only if the user explicitly requested a document, also build the DOCX described under DOCX Companion with the host's document toolchain ([host-adapters.md](references/host-adapters.md#building-documents)), from the **same reconciled figures** as the deck.

## Step 6: QA

After generating the file:

1. Run the host's presentation validation, then render every slide to an image with the host's render step ([host-adapters.md](references/host-adapters.md#rendering-and-inspecting-slides)). Use the full-resolution renders, not the thumbnail grid.
2. Open and inspect **every slide at full size** — check for clipping, overlapping text, awkward wrapping, chart errors, color-contrast issues, placeholder text or bracketed TODOs
3. Verify every data point, denominator and timestamp matches what the tools returned, and that the DOCX (if any) uses the same figures as the deck
4. If a DOCX was built, run the host's document-toolchain checks on it ([host-adapters.md](references/host-adapters.md#building-documents)) and confirm headings, tables and the Sources & Limits section render with no placeholder text
5. Confirm no slide shows a permission error, an "unavailable" metric rendered as zero, or per-rep detail on an executive-audience deck
6. Fix any issues, re-render the changed slides, and re-inspect
7. Deliver: return **one clickable link** to the PPTX (plus one to the DOCX only if it was requested), followed by a short note on the stated assumptions, material gaps and excluded access-gated metrics

## DOCX Companion (only on explicit request)

Produce a DOCX only when the user explicitly asks for a document. Build it with the host's document toolchain ([host-adapters.md](references/host-adapters.md#building-documents)), from the same reconciled figures as the deck (if the user asked for the document *instead of* a deck, still reconcile the figures the same way). Keep the same assumptions line, denominators, timestamps and Sources & Limits section. Structure it as:

```
QUARTERLY BUSINESS REVIEW — [Quarter] [Year]

1. Executive Summary
   [Narrative paragraph with headline and key themes]

2. Revenue Performance
   [Table: Metric | This Quarter | Last Quarter | Delta — constant-currency attainment row when FX is material]
   [Projected landing with basis and any fallback_reason]
   [Optional: Regional Performance — top-level regions plus Unassigned, from segment_performance_summary]
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
   [Table: Deal | Amount | Health Score / Band | Top Risk Factor | Qualification Note (MEDDPIC/BANT/SPICED, from opportunity_framework_summary)]
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

11. Sources & Limits
   [Tools, as-of timestamps, periods, currency; unavailable / access-gated / low-sample metrics; no error text]
```

## Tips for Great QBRs

- **Lead with insight, not data.** Every slide should answer "so what?" before showing numbers.
- **Use comparisons.** Raw numbers are meaningless without context — show quarter-over-quarter deltas, benchmark comparisons, and target vs actual.
- **Be honest about risk.** The credibility of your QBR depends on acknowledging what's not going well. Never hide a weak metric or invent a benchmark.
- **Keep the evidence attached.** Denominators, sample sizes, timestamps and caveats travel with every number.
- **End with clear actions.** The audience should leave knowing exactly what happens next.

## Guardrails

- Internal only. Customer-facing reviews → `customer-qbr`; board or investor packs → `board-revenue-pack`.
- Read-only: no `refresh: true`, no writes.
- Missing, empty or access-gated data is unavailable — never zero, never a positive signal.
- Never expose permission errors, rep-sensitive detail (per-rep rankings, individual completion or deal-mix on an executive deck) or unsupported customer claims on audience-facing slides.
- No causal language about health movement, interventions or execution signals.
- DOCX only on explicit request, built from the same reconciled figures.

## Final verification checklist

- [ ] Preflight checklist complete; `current_context` ran first; returned IDs match `scoped_org_id`
- [ ] Reporting period, comparison period, currency, audience and scope resolved and stated as assumptions
- [ ] Async envelopes polled to terminal; no processing envelope rendered as blank or zero
- [ ] Every rate shows its denominator or sample size; every source has an as-of timestamp
- [ ] Unavailable / access-gated metrics listed on Sources & Limits, with no error text
- [ ] Benchmarks shown only when a tool returned them
- [ ] Risk ordering uses `healthScore` / `healthBand`, not inverted `riskScore`
- [ ] Reporting currency read from the response and shown once on the title slide; no bare `$` (in text, helpers or chart axes) unless the reporting currency is USD
- [ ] Excluded or unconverted amounts disclosed beside the affected totals; no self-computed conversions
- [ ] Constant-currency `status` checked; FX discussion omitted for single-currency orgs; material FX effect shown as its own line on ARR and attainment, never as performance
- [ ] Projected landing shows its `basis` and any `fallback_reason`
- [ ] Regional slide (if any) only for an available dimension, includes the Unassigned row, no partial TAM sum
- [ ] Fixture rows excluded, or the demo label is on every slide
- [ ] Every slide rendered and inspected at full size; one link returned (two only if a DOCX was requested)
