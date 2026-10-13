---
name: "territory-review"
description: "Build a strategic territory planning or review deck (PPTX) from live Summit53 account, pipeline, health, activity, ARR, capacity and renewal evidence: sales-region and market-region performance, who sells where, TAM penetration, capacity per region, coverage questions and evidence-backed rebalancing options for CROs, VPs and regional leaders. Use for territory reviews, territory planning, geo or regional performance reviews, territory scorecards, whitespace analysis, prospecting allocation, territory health checks and rebalancing. Triggers: 'how are my territories doing', 'territory breakdown', 'where should we prospect', 'which territories are underperforming', 'regional pipeline review', 'show me territory coverage', 'how penetrated are we in each market', 'who is selling into which region'. Do not use for individual rep coaching — use rep-coaching-report. Do not use for a board or investor pack — use board-revenue-pack."
version: "1.2.0"
baselined: "2026-10-13"
status: "active"
---

# Territory Review

Build a decision-ready territory review deck from live Summit53 evidence: where to double down, where to intervene, and which coverage questions need validating, with explicit limits wherever territory fields are incomplete.

## Route first

- Individual rep coaching or 1:1 prep → `rep-coaching-report`.
- Board or investor revenue pack → `board-revenue-pack`.
- Everything else about territories, regions, geos, segments or owner books stays here.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its checklist before any data call. Load every tool named in Step 2 in one ToolSearch `select:` call if they are deferred.

Skill-specific gates:

- **Demo label.** This is a commercial artifact. If fixture rows cannot be separated, label the whole deck **Demo data — not for customer or commercial decisions**.
- **Territory basis defined** (Step 1) before any territory-level number is computed.
- **Period, comparison baseline and currency resolved** before analysis. Never mix currencies inside one comparison.
- **Audience resolved.** Rep-level detail (named reps, ramp status per rep, capacity per person) appears only when the requested audience is authorized to see it and the detail is necessary for the recommendation. Default to territory-level aggregates.
- **Read-only.** Never pass `refresh: true` (for example to `segment_performance_summary`). This skill writes nothing.

- **Optional enhancements stay optional.** Region dimensions, cross-tabs, TAM, region-grouped capacity and ICP fit are enhancements. If a capability is absent from the live schema, access-denied or plan-gated, continue without it and state the gap in the closing limits (preflight §5).

Read [references/async-envelopes.md](references/async-envelopes.md) before calling `unified_forecast_summary`; it can return a processing envelope instead of data.

Read [references/currency-and-fx.md](references/currency-and-fx.md) before formatting any amount or comparing regions: it covers reporting-currency labels, excluded unconverted amounts, constant currency and `native_by_currency` for regions that trade in more than one currency.

## Step 1: Clarify scope and define the territory basis

Confirm these with the user (use the defaults if they say "just do it"):

- **Territories of interest**: all, or named ones. Default: all.
- **Time period and baseline**: default current quarter vs previous quarter.
- **Currency**: the org's reporting currency unless the user names another.
- **Audience**: CRO/leadership (strategic, aggregated) or regional managers (operational). Default: CRO.
- **Special focus**: territories, segments or accounts to highlight.

**Define the territory basis before analysis.** A "territory" is one of: geography (sales or market region), named-account list, owner book, segment, or another user-defined grouping.

**Select the basis from what the org supports.** Call `arr_operating_summary` first (no `refresh`) and read `by_dimension.dimension_options`:

| Option | Meaning | Available when |
|---|---|---|
| `segment` | Customer segment | `segment.available` |
| `sales_region` | Sales Org team tree — who sells | `sales_region.available` (`region_team_count`, `team_count` show how much of the team tree is regional) |
| `market_region` | Geographic market tree — where customers are | `market_region.available` (`leaf_count` markets) |

Pick the basis from the user's request plus availability: "regions", "teams", "who sells" → `sales_region`; "geo", "markets", "countries", "TAM", "penetration" → `market_region`; "segments" → `segment`. With no steer, prefer `sales_region` when available (it matches how capacity and quota are owned), else `market_region`, else `segment`. If the requested basis is unavailable, say so and use the next best one. Both region dimensions are trees: call with `level: "top"` for the rollup and `level: "leaf"` for the drill-down.

Disclose the basis, its `dimension_source` and the level on Slide 2 and in the closing limits ("Territory basis: Sales Org regions (top level, drill-down to leaf teams)"). If no dimension is available and `account_intelligence_summary` has no territory breakdown, derive groupings **only from explicit account attributes** (region, country, owner, segment) and disclose: "No authoritative territory field — territories derived from {attribute}." Never infer a territory from an account name, a domain, or free text.

## Step 2: Pull the data

Run independent reads in parallel. Inspect each tool's live schema first; argument names below are semantic guidance.

0. **ARR by territory and the basis gate** — `arr_operating_summary` (already called in Step 1) with `dimension` and `level` set to the basis: `by_dimension{groups, unassigned, tree, rollup}` gives ARR stock, bookings and retention per group. Read `metadata.currency` here and on every revenue response.
1. **Account intelligence by territory** — `account_intelligence_summary`. Primary source: `territory_summary`, `territory_metrics.account_penetration`, `territories_with_low_penetration`, `value_segments`, `health_distribution`. Money is in the reporting `currency` with an `fx` block. Call unfiltered first; if specific territories were requested, also call with `territories: [list]`. When the live schema exposes `icp_fit_distribution` and per-row `icp_fit_rating` / `icp_fit_score` (optional, pending rollout), keep them for the fit mix (Step 4).
2. **Region performance** — `segment_performance_summary` with `dimension` set to the basis. When the basis is a region, call `level: "top"` for the rollup, then `level: "leaf"` for the drill-down. Region views return `groups[]`, `unassigned`, `tree[]` (`group_id`, `node_type`, `parent_group_id`, `depth`, `path`, `child_group_ids`), `strongest_groups` / `weakest_groups` and `dimension_source`. Market rows carry `tam` and `tam_currency`; the `unassigned` row carries `accounts_missing_market`. Rows can carry `metrics.native_by_currency`. Requires analytics permission. Do not pass `refresh`.
   - **Cross-tabs** (optional) — when both `sales_region` and `market_region` are available, call `segment_performance_summary` with `dimension: "sales_region"`, `secondary: "market_region"` to get `crosstab{rows, columns, cells, row_totals, column_totals, grand_total}` plus `home_markets{row: {group_ids, source}}` (source `rep_market_assignment`, `largest_share` or `none`) and `cross_market{row: [columns]}`. When segment mix may explain a region gap, also call `dimension: <region basis>`, `secondary: "segment"`. `secondary` must differ from `dimension`; every cross-tab carries an Unassigned row and column.
3. **Pipeline risk distribution** — `pipeline_risk_summary`: pipeline value distribution, risk levels and confidence across the book.
4. **Deal-level health** — `risk_heatmap` (`page_size: 25`, `sort_by: "healthScore"`, `sort_direction: "asc"`). Treat `score_semantics` and the tool's own description as authoritative: `healthScore` is a **0.0–1.0** value and **higher is healthier**, so riskiest-first is ascending. `riskScore` / `risk_score` are only deprecated sorting aliases with the **same** direction — never sort them descending and never read them as "higher = riskier". Prefer each row's server-supplied `healthBand` over any hand-rolled threshold. `risk_heatmap` has no territory filter: map deals to territories through their account.
5. **Activity gaps** — `activity_gaps` (`days: 30`, `limit: 25`). Map dormant accounts to territories through the account data. Dormant accounts in high-value territories matter most.
6. **ARR growth** — `arr_growth_analytics` with `include_trends`, `include_changes`, `include_benchmarks` all `true`.
7. **Forecast** — `unified_forecast_summary` (`period_offset: 0`): pipeline coverage, quota tracking, team metrics. It also returns `kpis.pipeline_coverage.by_deal_size` (org-adaptive deal-size bands), `kpis.win_rate.by_deal_size`, and `kpis.pipeline_coverage.acv_drift` (`drift_pct`, `direction`, `is_significant`). It is asynchronous on a cold cache: poll `get_job` to terminal per [references/async-envelopes.md](references/async-envelopes.md), then re-call with identical arguments. Resolve it once and reuse the payload. Also call `forecast_confidence` (confidence, velocity, stage distribution).
8. **Capacity vs target** — `capacity_to_target_planner` with `group_by` set to the region basis (`sales_region` or `market_region`) and the same `level`; fall back to `team` and/or `sales_role` when the basis is not a region or the region grouping is unavailable. Separates capacity-constrained territories (not enough reps) from execution-constrained ones (enough reps, target still at risk). Read its `warnings` (Step 4, "Capacity per region"). Feeds Slide 3. Permission-gated.
9. **Reverse capacity** — `reverse_capacity_planner`, grouped the same way. Converts an Intervene territory's gap-to-target into a headcount estimate. Feeds Slide 10. Permission-gated.
10. **Renewal defence** — `renewal_forecast_summary`: ARR renewing in the next 30–180 days and at-risk renewal ARR, ideally by territory. Feeds Slide 5. Permission-gated.
11. **Ramp cohort** — `ramp_cohort`: reps still inside their ramp window. Use it before calling any territory "underperforming". Permission-gated; check the live schema for roster-level vs per-rep arguments and filter locally if it is roster-level.
12. **Hunter/farmer mix** — `hunter_farmer_mix`: new-business vs expansion mix per territory. Feeds Slide 3. Permission-gated; same schema check as `ramp_cohort`.
13. **Account health movement** — `account_health_movement`: accounts trending healthy → at-risk → critical (or back) per territory over the period. Feeds Slide 6. Permission-gated. Movement is **correlational**: accounts "moved" or "trended", never "a territory or rep caused".
14. **Coverage caveats** — `data_quality_score`: `issues.accounts_missing_country` and deal-currency-without-rate counts. These bound how complete any market-region view can be. Feeds Slide 2 and the coverage questions.
15. **Account ICP fit** (optional, pending rollout) — only when `search_accounts` exposes `icp_fit{rating, score, icp_version, source, scored_at}` and the `icp_fit_rating` filter: pull strong- and good-fit accounts and map them to territories through explicit account attributes. If the schema lacks it, skip and note "Account ICP fit not available on this connector."

### Handling missing data

Adapt; do not fail. A missing value is **unavailable**, never zero or healthy (preflight §5).

- No territory breakdown from `account_intelligence_summary` or `segment_performance_summary` → use the Step 1 fallback (explicit account attributes only) and disclose it.
- ARR growth with no territory breakdown → show the aggregate and label it company-wide.
- `activity_gaps` returns an empty list → report "No dormant accounts returned for the {days}-day window" and treat it as **indeterminate** unless the tool marks the empty result as verified. Never render it as "all territories engaged".
- A territory with zero accounts or zero pipeline **in the CRM** → absence of CRM records is not proof of whitespace. Flag it as a **coverage question to validate with market data** (addressable accounts, firmographic lists, external research), not as an opportunity.
- `dimension_options` missing or a region dimension unavailable → skip the region tree, cross-tab and TAM views and use the next basis from Step 1. `segment_performance_summary` denied (analytics permission) → use `arr_operating_summary` groups for ARR and drop the period-aware pipeline/velocity per region.
- `capacity_to_target_planner`, `reverse_capacity_planner`, `renewal_forecast_summary`, `ramp_cohort`, `hunter_farmer_mix` and `account_health_movement` are manager/team-permission gated. If one is unauthorized or empty, drop only the enhancement it feeds (capacity badge, headcount estimate, renewal panel, ramp adjustment, hunter/farmer line, movement view) and fall back as described per slide. Summarise gaps in the closing limits; never show raw permission errors.

## Step 3: Reconcile records to territories

Before computing any indicator:

1. Assign every account and opportunity to exactly one territory using the Step 1 basis. When the basis is a server dimension (`segment`, `sales_region`, `market_region`), the server's groups and its `unassigned` row are the assignment — do not re-derive them from account attributes.
2. Track **unassigned** records (no value in the territory attribute) and **ambiguously assigned** records (conflicting values, e.g. account region ≠ owner region, or multiple matches) **separately**. Never fold them into the nearest territory or drop them silently.
3. Report the count and value of unassigned/ambiguous records on Slide 2. The Unassigned row is **always shown**, even when small; for `market_region` show its `accounts_missing_market` beside it. If unassigned/ambiguous records exceed ~10% of accounts, ARR or pipeline value, say so in the headline limits: territory comparisons are partial.
4. Exclude fixture rows per the preflight before counting anything.

## Step 4: Analyse territory patterns

Synthesise before building slides. Preserve denominators and sample sizes on every indicator ("4 of 11 accounts", not just "36%").

### Normalise before comparing

Territories differ in size, segment mix, tenure and staffing. Do not compare raw totals across unlike territories. Compare on normalised measures: pipeline per account or per rep, coverage ratio vs that territory's own target, ARR share vs account share, win rate within the same deal-size band, health mix as a proportion. If two territories are not comparable even after normalisation (for example one is enterprise named-accounts and the other is SMB geography), say so and compare each to its own baseline instead.

### Territory scoring

For each territory:

1. **Revenue concentration** — share of total ARR. Over-indexed on one territory?
2. **Pipeline coverage** — pipeline vs that territory's target or quota. Which are pipeline-starved?
3. **Account health distribution** — healthy / at-risk / critical counts and proportions, from the server's categories.
4. **Engagement** — dormant accounts and the ARR attached to them.
5. **Deal health density** — count and value of deals in the server's `Low` `healthBand`, and the median `healthScore` (lower = less healthy). Do not average a deprecated `riskScore` as if higher meant riskier.
6. **Capacity vs execution** — from `capacity_to_target_planner`: understaffed (headcount question) vs execution-constrained (coaching/process question).
7. **Ramp-adjusted performance** — cross-check apparent underperformers against `ramp_cohort`. A territory with several reps still ramping is judged against ramp-stage expectations before anything is labelled "underperforming".

### Region tree: rollup, then drill-down

When the basis is a region dimension:

- Lead with the `level: "top"` rollup (one row per top-level region), then drill into `level: "leaf"` children using `tree[]` (`parent_group_id`, `child_group_ids`, `path`) so each leaf sits under its parent. Do not add leaf rows to rebuild a parent; use the server's rollup.
- Use the server's `strongest_groups` / `weakest_groups` as the starting point for "where to double down / intervene", then confirm against the normalised measures above. Say which metric the server ranked on.
- Show the **Unassigned** row at both levels with its value, and `accounts_missing_market` for market regions.

### Who sells where (cross-tab)

From the `sales_region` × `market_region` cross-tab:

- Read each sales region's row across markets: where its ARR and pipeline actually sit. Use `row_totals`, `column_totals` and `grand_total` for shares; do not recompute totals from cells.
- Flag `cross_market` cells — a sales region selling outside its home market — against `home_markets` and name the `source`: `rep_market_assignment` (from rep territory assignments: reliable), `largest_share` (inferred from where the region sells most: an approximation), or `none` (no home market known: do not call anything cross-market for that row). Cross-market selling is a **pattern to discuss** (overlap, channel conflict, deliberate coverage), not a violation.
- Unassigned row/column: deals or accounts with no sales region or no market. Show them; they bound how far the cross-tab can be trusted.
- When a region gap might be a mix effect, use the region × `segment` cross-tab to compare like segments across regions before blaming execution.

### TAM and penetration

Market rows carry `tam` and `tam_currency`. Penetration is the row's booked ARR (or open pipeline) as a share of its TAM.

- Label TAM in its `tam_currency`. Convert nothing yourself.
- Compute a share only when `tam_currency` equals the reporting currency of the ARR/pipeline figure. If they differ, show both figures side by side, each in its own currency, and write "ratio not computed — TAM in {tam_currency}, ARR in {reporting currency}".
- A parent market's TAM is **unknown** if any child TAM is missing: never sum a partial set of children. A missing TAM is "TAM not set", not zero.
- Pair it with `account_intelligence_summary` `territory_metrics.account_penetration` and `territories_with_low_penetration` — a different measure (account penetration, not revenue share of TAM); label each by name.
- TAM is the org's own input, not market evidence; cite it as "TAM as configured in Summit53".

### Capacity per region

When `capacity_to_target_planner` / `reverse_capacity_planner` were called with `group_by: "sales_region"` or `"market_region"`, read the per-group figures and surface every warning beside them:

| Warning | What it means for the reader |
|---|---|
| `region_grouping` | Capacity is grouped by region; always present on region views. Name the grouping. |
| `owner_profile_attribution` | Open pipeline follows the owner's **current** team, so moved reps carry their pipeline with them. |
| `market_quota_unassigned` | Some quota counts toward no market — a rep's quota only counts toward a market when the rep is assigned to that market's territory. Market targets are understated. |
| `reps_without_team` | Some quota-carrying reps have no sales team, so their quota sits in Unassigned. |
| `org_seller_average_quota_fallback` (assumption source) | A group has no sellers; its AE quota is the org-wide average. Treat that group's headcount estimate as indicative. |

These replace the qualitative-only capacity read when they are available. If region grouping is unavailable, fall back to `team` / `sales_role` and say capacity is not region-aligned.

### Currency across regions

Follow [references/currency-and-fx.md](references/currency-and-fx.md). Every amount carries the reporting-currency label. Where a region trades in more than one currency, use `metrics.native_by_currency` to show the foreign share (e.g. "EMEA: 62% of new ARR booked in EUR"); never sum native amounts across currencies. If `fx_unconverted_amounts_excluded` is present, name the excluded amounts beside the affected region and mark any ranking it could change as provisional. When constant-currency figures are available, separate FX effect from regional performance.

### Coverage questions and expansion

Identify:

- Territories with little or no CRM revenue or pipeline → **coverage questions** to validate with market data. Absence of records is not evidence of untapped demand.
- Low penetration of a configured TAM, or low account counts relative to an externally known market size (only when that market size comes from a cited source).
- Data gaps that hide coverage: `data_quality_score` `issues.accounts_missing_country`, the Unassigned rows and `accounts_missing_market`, and deal currencies without a rate. Turn them into "coverage questions to validate" ("41 accounts have no country, so market coverage for APAC may be understated").
- Existing accounts with no active pipeline.
- Healthy accounts with no expansion motion underway (expansion candidates from `account_intelligence_summary`).

**ICP fit mix** (optional, pending rollout — only when `search_accounts` exposes `icp_fit` or `account_intelligence_summary` exposes `icp_fit_distribution`): show the strong / good / moderate / weak / unknown mix per territory with counts. Frame the sharpest coverage questions as **strong- or good-fit accounts with low coverage** (no open pipeline, dormant, or low penetration) — these are fit-weighted whitespace **hypotheses**, still not proof of whitespace. `unknown` means never scored, not weak: report it as its own share and never fold it into weak. Note the `icp_version` when ratings were scored on different ICP versions.

### Recommendations: evidence vs hypothesis

Generate 3–5 territory-level recommendations. Label each one:

- **Evidence-backed** — supported by the pulled data with stated denominators (e.g. "West holds 35% of accounts (41 of 117) but 18% of pipeline value").
- **Hypothesis to validate** — depends on market potential, coverage, or causal assumptions the CRM cannot confirm (e.g. "Closing West's coverage gap could add pipeline — validate addressable accounts first"). State what evidence would confirm or refute it.

Each recommendation names a concrete action and the outcome it targets. For **Intervene** items, prefer a headcount estimate from `reverse_capacity_planner` when available over vague effort-shift language.

**No reassignment advice from raw pipeline alone.** Before recommending that accounts, reps or effort move between territories, weigh capacity, account potential, renewal exposure, engagement and ownership constraints. If only pipeline totals are available, frame it as a hypothesis, not a reassignment.

Avoid generic advice like "improve territory coverage".

## Step 5: Build the deck

Build with PptxGenJS following the `pptx` skill: read its SKILL.md and its `pptxgenjs.md` reference before writing code. Use the **Midnight Executive** design system for consistency with other Summit53 decks.

### Design system

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
| Unavailable / neutral | Slate | `64748B` |
| Light Slate (dividers, grid) | Light Slate | `E2E8F0` |
| Good ICP fit (fit mix only) | Light Emerald | `34D399` |

**Typography**: Georgia headers (36–44pt), Calibri body (14–16pt).
**Layout**: 16:9 widescreen, 0.5" minimum margins. Dark title/close slides, light content slides. If a demo label applies, put it on every slide.

### Slide structure (up to 11 slides, ~25-minute review)

Slide 4 appears only when the `sales_region` × `market_region` cross-tab is available; without it the deck is 10 slides and later slides move up one (slide numbers in this file assume it is present). Adjust the composition when the number of territories or data density needs it; keep the content contract.

#### Slide 1: Title
- Navy background. "Territory Review", period label, date, organization name, "Powered by Summit53". Centered; large Georgia title, Calibri subtitle.

#### Slide 2: Territory overview and basis
- Sources: `arr_operating_summary` (`by_dimension`), `account_intelligence_summary` (`territory_summary`), `segment_performance_summary` (`level: "top"`), `unified_forecast_summary`, `data_quality_score`.
- Four stat cards: territories active, accounts under management, pipeline value, aggregate ARR (reporting-currency labels).
- Below: one row per **top-level** territory (account count, pipeline, ARR, account-health mix), with the server's strongest/weakest groups marked. Left border colour comes from the server's health categories via `healthColor()`; slate when unavailable.
- An **Unassigned / ambiguous** row, always shown, with its counts and value (Step 3) and `accounts_missing_market` for market regions.
- Basis and coverage note: "Territory basis: {basis} ({dimension_source}, {level}). {N} unassigned, {M} ambiguous records shown separately. {k} accounts have no country; {c} deal currencies have no rate."

#### Slide 3: Territory scorecards
- Sources: `segment_performance_summary` (`level: "leaf"`), `account_intelligence_summary`, `capacity_to_target_planner`, `ramp_cohort`, `hunter_farmer_mix`.
- One card per leaf territory (2×2 or 2×3), grouped under its parent from `tree[]`: name, account count, pipeline, ARR, health mix (server categories), active deal count, a one-line new-business vs expansion split from `hunter_farmer_mix` (omit if unavailable), and a **capacity verdict** badge — "On track to hit target", "Capacity-constrained" or "Execution-constrained". Omit the badge if the tool is unauthorized or empty; never guess.
- Capacity warnings (`market_quota_unassigned`, `reps_without_team`, `owner_profile_attribution`, quota fallback) as a footnote on the cards they affect.
- More than 6 territories → show the top 6 by ARR and state how many more exist.
- Before flagging a card red, check `ramp_cohort`. If a meaningful share of the territory's reps are ramping, note it on the card (e.g. "2 of 4 AEs ramping — judged against ramp plan"). Named reps only for authorized audiences.

#### Slide 4: Who sells where (conditional)
- Source: `segment_performance_summary` with `dimension: "sales_region"`, `secondary: "market_region"`; optionally the region × `segment` cross-tab.
- Heat-table: sales regions as rows, markets as columns, ARR or pipeline per cell (state which), row/column totals from the server, and the Unassigned row and column. Shade by share of row total.
- Mark `cross_market` cells with an outline and a legend: "Outside home market (home market source: {source})". Rows with `source: none` get no cross-market marks and a "home market unknown" note.
- One callout: the largest cross-market share, framed as a coverage pattern to discuss, not a violation. If the segment cross-tab explains a region gap, add one line on it.

#### Slide 5: Pipeline distribution by territory
- Sources: `unified_forecast_summary`, `forecast_confidence`, `pipeline_risk_summary`, `renewal_forecast_summary`.
- Bar chart (stacked by stage or risk level) of pipeline per territory, then a table: Territory | Pipeline | Target | Coverage ratio. Coverage colour via `coverageColor()`: below 2× red, 2–3× amber, 3×+ emerald; slate if target unavailable.
- **Deal-size composition**: mini-chart from `kpis.pipeline_coverage.by_deal_size`. If `acv_drift.is_significant` is `true`, add one amber line: "Pipeline ACV is drifting {direction} {drift_pct}% vs trailing-12-month closed-won — pipeline deals no longer resemble what the team has historically closed." Omit when not significant.
- **Renewal defence** panel from `renewal_forecast_summary`: ARR renewing in 30–180 days and at-risk renewal ARR per territory. If unavailable: "Renewal defence data unavailable — showing new pipeline only."

#### Slide 6: Account health by territory
- Sources: `account_health_movement` (primary), `account_intelligence_summary` `health_distribution` (snapshot/fallback).
- Lead with movement: accounts that trended healthy → at-risk and at-risk → critical per territory. Pair with the healthy / at-risk / critical distribution (counts and proportions). Below: top 5 at-risk accounts — Account, Territory, Health, ARR, Primary risk factor.
- Correlational language only. If movement is unavailable: "Health movement unavailable — showing point-in-time snapshot."
- Answers: "Where are accounts most vulnerable, and which territories are trending the wrong way?"

#### Slide 7: Market penetration, coverage questions and expansion
- Sources: `segment_performance_summary` market rows (`tam`, `tam_currency`), `account_intelligence_summary` (`territory_metrics.account_penetration`, `territories_with_low_penetration`, expansion candidates, optional `icp_fit_distribution`), `data_quality_score`, optional `search_accounts` `icp_fit`.
- Top strip — **penetration table** (market regions only, when any TAM is set): Market | TAM ({tam_currency}) | ARR | Pipeline | Share of TAM | Account penetration. Share via `penetrationShare()`; "TAM not set", "parent TAM unknown (partial children)" or "ratio not computed — currencies differ" where it applies. Omit the strip when no TAM is configured and say so in the limits.
- Two columns below:
  - **Left — "Coverage questions to validate"** (navy accent): territories with little or no CRM revenue/pipeline or low penetration, data gaps that hide coverage (accounts missing country, Unassigned rows), and — when ICP fit is available — strong/good-fit accounts with low coverage per territory, with the fit mix (including `unknown`) as counts. State the market evidence needed to confirm real whitespace. Never title this column "untapped" or "whitespace" unless external market evidence is cited.
  - **Right — "Expansion opportunities"** (emerald accent): healthy existing accounts with room to grow, from `account_intelligence_summary` expansion candidates.

#### Slide 8: Engagement gaps by territory
- Source: `activity_gaps`.
- If dormant accounts were returned: amber callout with count and ARR attached, then a table grouped by territory (Account, Territory, Days since last activity, ARR). Highlight the territories with the most dormant accounts.
- If the list is empty: a **neutral** (slate) note — "No dormant accounts returned for the {days}-day window." Do not use a green "all engaged" callout; no logged activity and no returned gap are both indeterminate without a verified-zero flag.

#### Slide 9: Deal health by territory
- Sources: `risk_heatmap`, `pipeline_risk_summary`.
- Table of the least healthy deals, annotated by territory: Deal, Territory, Amount, Stage, Health score, Health band, Top risk factor. Colour from the server's `healthBand` via `healthBandColor()`: `Low` → red, `Medium` → amber, `High` → emerald, missing → slate "band unavailable". Order by `healthScore` ascending. Cap at 10 rows; navy header row, white text.
- Callout: which territory carries the most `Low`-band deal value (with count and denominator).

#### Slide 10: Territory recommendations
- Sources: Step 4 recommendations; `reverse_capacity_planner` for Intervene items.
- 3–5 numbered recommendations (emerald numbered circles), each with a bold action headline, one supporting sentence (evidence with denominators, expected outcome), and a tag: **Evidence-backed** or **Hypothesis to validate**.
- Group as **Double down** (performing territories), **Intervene** (needing attention), **Explore** (coverage questions; these are hypotheses by default, including fit-weighted ones).
- For each Intervene item, translate the gap into a headcount estimate where `reverse_capacity_planner` is available, grouped by the same region basis (e.g. "West: ~1.4 additional AEs estimated to reach target"), and carry its capacity warnings. Otherwise use qualitative effort-shift language. No reassignment advice from raw pipeline alone.

#### Slide 11: Close — basis, sources and limits
- Navy background. Title: "Territory Strategy: Where We Play, How We Win", organization name, date.
- Lower block (Ice Blue text): territory basis and level, period and reporting currency (with any excluded unconverted amounts), unassigned/ambiguous counts, coverage caveats, capacity warnings, sources used, sources and optional capabilities unavailable (summarised, no raw errors), and the demo label if it applies.

## Step 6: Generate the file

Write one Node.js PptxGenJS script that:

1. Embeds all pulled and calculated data directly (no external data files).
2. Uses factory functions for shadows and option objects (PptxGenJS mutates option objects; never reuse them across calls).
3. Defines helpers: `addStatCard()`, `addSectionTitle()`, `healthBandColor()`, `healthColor()`, `coverageColor()`, `formatCurrency()`, `penetrationShare()`, `fitColor()`, `crosstabCell()`, `territoryCard()`.
4. Builds every slide above.
5. Handles missing data, empty arrays, nulls and unassigned records, rendering "unavailable" rather than `0`.
6. Saves to the session's outputs directory as `Territory-Review-[Date].pptx`.

### Helper patterns

```javascript
// Deal health colour. Follow the server's healthBand; never derive colour from raw score thresholds.
// healthScore is 0.0–1.0 and higher = healthier; riskScore is a deprecated alias with the SAME direction.
function healthBandColor(band) {
  const map = { low: "EF4444", medium: "F59E0B", high: "10B981" };
  return map[String(band ?? "").toLowerCase()] || "64748B"; // slate = band unavailable
}

// Account health colour from the server's health category.
function healthColor(status) {
  const map = { healthy: "10B981", "at-risk": "F59E0B", critical: "EF4444" };
  return map[String(status ?? "").toLowerCase()] || "64748B";
}

// Coverage ratio colour; slate when the target (and so the ratio) is unavailable.
function coverageColor(ratio) {
  if (ratio == null || Number.isNaN(ratio)) return "64748B";
  if (ratio >= 3) return "10B981";
  if (ratio >= 2) return "F59E0B";
  return "EF4444";
}

// Fresh shadow object per call (avoids the PptxGenJS mutation issue).
const makeShadow = () => ({ type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.15 });

// Reporting currency comes from the response (metadata.currency or top-level currency), never assumed.
// Null renders as "unavailable", never 0. Bare "$" only for USD with a US-only audience.
const CURRENCY_PREFIX = { USD: "US$", NZD: "NZ$", AUD: "A$", CAD: "C$", SGD: "S$", EUR: "€", GBP: "£" };
function formatCurrency(val, code, { usOnly = false } = {}) {
  if (val == null || Number.isNaN(val)) return "unavailable";
  const prefix = code === "USD" && usOnly ? "$" : (CURRENCY_PREFIX[code] ?? `${code} `);
  if (Math.abs(val) >= 1e6) return `${prefix}${(val / 1e6).toFixed(1)}M`;
  if (Math.abs(val) >= 1e3) return `${prefix}${(val / 1e3).toFixed(0)}K`;
  return `${prefix}${val}`;
}

// Share of TAM. Never converts and never computes across currencies; a parent TAM that the
// server leaves null (partial children) stays unknown — never sum children to fill it.
function penetrationShare(amount, amountCurrency, tam, tamCurrency) {
  if (tam == null) return { text: "TAM not set", value: null };
  if (amount == null) return { text: "unavailable", value: null };
  if (tamCurrency !== amountCurrency) {
    return { text: `ratio not computed — TAM in ${tamCurrency}, ARR in ${amountCurrency}`, value: null };
  }
  const value = amount / tam;
  return { text: `${(value * 100).toFixed(1)}% of TAM`, value };
}

// ICP fit colour. "unknown" means never scored — slate, never the weak colour.
function fitColor(rating) {
  const map = { strong: "10B981", good: "34D399", moderate: "F59E0B", weak: "EF4444" };
  return map[String(rating ?? "").toLowerCase()] || "64748B";
}

// Cross-tab cell: shade by share of the server's row total; outline cells the server flags as cross_market.
function crosstabCell(value, rowTotal, isCrossMarket) {
  const share = rowTotal ? value / rowTotal : null;
  const fill = share == null ? "F8FAFC" : share >= 0.4 ? "1E2761" : share >= 0.15 ? "CADCFC" : "F8FAFC";
  return {
    fill: { color: fill },
    color: fill === "1E2761" ? "FFFFFF" : "1E293B",
    border: isCrossMarket ? { type: "dash", pt: 1.5, color: "F59E0B" } : { type: "solid", pt: 0.5, color: "E2E8F0" },
  };
}
```

## Step 7: Render, QA and deliver

1. Render **every** slide to an image using the `pptx` skill's render/thumbnail flow (or `soffice --headless --convert-to pdf` then `pdftoppm -jpeg -r 150`).
2. Inspect each slide at full size: overlap, clipping, wrapping, chart scales, mislabelled territories, placeholder text, colour contrast.
3. Spot-check every headline number against the source payloads, including the unassigned/ambiguous counts.
4. Fix and re-render until clean.
5. Return **one clickable link** to the PPTX, followed by a short note on territory basis, coverage limitations, unavailable sources and anything excluded.

## Tips for great territory reviews

- **Lead with the allocation question.** Every slide should help answer "where should we put resources?"
- **Make coverage questions actionable.** Don't just say "Territory X has no revenue" — show what the CRM holds there and what market evidence would confirm the opportunity.
- **Balance defence and offence.** Quantify renewal risk as hard as new pipeline.
- **Be honest about concentration risk.** If 80% of ARR sits in one territory, that is the headline.
- **Don't penalise ramp.** Check `ramp_cohort` before branding a territory underperforming.
- **Use the region model the org has.** Read `dimension_options` first; roll up, then drill down; always show Unassigned.
- **Read capacity warnings before headcount.** `market_quota_unassigned` or `reps_without_team` can make a region look under-quota'd when it is an assignment gap.
- **Make Intervene asks concrete** — a headcount estimate beats a vague effort shift — and keep hypotheses labelled as hypotheses.
- **Keep it to 10 slides, 11 with the cross-tab.**

## Verification checklist

- [ ] Preflight checklist complete; `scoped_org_id` matched on returned data
- [ ] `dimension_options` read first; territory basis, `dimension_source` and level stated; derived groupings disclosed
- [ ] Region views roll up (top) then drill down (leaf); parents not rebuilt by summing children
- [ ] Unassigned row shown at every level, with `accounts_missing_market` for markets; `accounts_missing_country` and unrated deal currencies raised as coverage questions
- [ ] Cross-market cells flagged only against `home_markets`, with the source named; `none` rows unflagged
- [ ] TAM labelled in `tam_currency`; no share across currencies; no partial parent TAM summed
- [ ] Capacity grouped by region where available, with every planner warning surfaced
- [ ] Reporting currency labelled per [references/currency-and-fx.md](references/currency-and-fx.md); excluded unconverted amounts disclosed; no native amounts summed across currencies
- [ ] ICP fit (if exposed) shown as a mix with `unknown` separate; fit-weighted gaps labelled hypotheses
- [ ] Unassigned and ambiguous records counted separately
- [ ] Comparisons normalised; denominators shown
- [ ] Deal colours follow server `healthBand`; no raw-threshold or inverted colouring
- [ ] No "whitespace" claim from absent CRM records; empty `activity_gaps` not shown as green
- [ ] Every recommendation tagged evidence-backed or hypothesis; no reassignment from raw pipeline alone
- [ ] Rep-level detail only for an authorized audience
- [ ] Demo label applied if fixtures could not be excluded
- [ ] Every slide rendered and inspected; one link returned
