---
name: "territory-review"
description: "Build a strategic territory planning or review deck (PPTX) from live Summit53 account, pipeline, health, activity, ARR, capacity and renewal evidence: territory scorecards, coverage, engagement gaps, coverage questions and evidence-backed rebalancing options for CROs, VPs and regional leaders. Use for territory reviews, territory planning, geo or regional performance reviews, territory scorecards, whitespace analysis, prospecting allocation, territory health checks and rebalancing. Triggers: 'how are my territories doing', 'territory breakdown', 'where should we prospect', 'which territories are underperforming', 'regional pipeline review', 'show me territory coverage'. Do not use for individual rep coaching — use rep-coaching-report. Do not use for a board or investor pack — use board-revenue-pack."
version: "1.1.0"
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

Read [references/async-envelopes.md](references/async-envelopes.md) before calling `unified_forecast_summary`; it can return a processing envelope instead of data.

## Step 1: Clarify scope and define the territory basis

Confirm these with the user (use the defaults if they say "just do it"):

- **Territories of interest**: all, or named ones. Default: all.
- **Time period and baseline**: default current quarter vs previous quarter.
- **Currency**: the org's reporting currency unless the user names another.
- **Audience**: CRO/leadership (strategic, aggregated) or regional managers (operational). Default: CRO.
- **Special focus**: territories, segments or accounts to highlight.

**Define the territory basis before analysis.** A "territory" is one of: geography (sales or market region), named-account list, owner book, segment, or another user-defined grouping. Use the org's authoritative territory field when one exists (`account_intelligence_summary` territory breakdown, or `segment_performance_summary` with `dimension: "sales_region"` / `"market_region"`). If there is no authoritative territory field, derive groupings **only from explicit account attributes** (region, country, owner, segment) and disclose on Slide 2 and in the closing limits: "No authoritative territory field — territories derived from {attribute}." Never infer a territory from an account name, a domain, or free text.

## Step 2: Pull the data

Run independent reads in parallel. Inspect each tool's live schema first; argument names below are semantic guidance.

1. **Account intelligence by territory** — `account_intelligence_summary`. Primary source: `territory_summary`, `value_segments`, `health_distribution`. Call unfiltered first; if specific territories were requested, also call with `territories: [list]`.
2. **Segment and region performance** (optional) — `segment_performance_summary` with `dimension` set to the territory basis (`sales_region` or `market_region`) when that is the basis. Period-aware ARR, pipeline, velocity and retention per region. Do not pass `refresh`.
3. **Pipeline risk distribution** — `pipeline_risk_summary`: pipeline value distribution, risk levels and confidence across the book.
4. **Deal-level health** — `risk_heatmap` (`page_size: 25`, `sort_by: "healthScore"`, `sort_direction: "asc"`). Treat `score_semantics` and the tool's own description as authoritative: `healthScore` is a **0.0–1.0** value and **higher is healthier**, so riskiest-first is ascending. `riskScore` / `risk_score` are only deprecated sorting aliases with the **same** direction — never sort them descending and never read them as "higher = riskier". Prefer each row's server-supplied `healthBand` over any hand-rolled threshold. `risk_heatmap` has no territory filter: map deals to territories through their account.
5. **Activity gaps** — `activity_gaps` (`days: 30`, `limit: 25`). Map dormant accounts to territories through the account data. Dormant accounts in high-value territories matter most.
6. **ARR growth** — `arr_growth_analytics` with `include_trends`, `include_changes`, `include_benchmarks` all `true`.
7. **Forecast** — `unified_forecast_summary` (`period_offset: 0`): pipeline coverage, quota tracking, team metrics. It also returns `kpis.pipeline_coverage.by_deal_size` (org-adaptive deal-size bands), `kpis.win_rate.by_deal_size`, and `kpis.pipeline_coverage.acv_drift` (`drift_pct`, `direction`, `is_significant`). It is asynchronous on a cold cache: poll `get_job` to terminal per [references/async-envelopes.md](references/async-envelopes.md), then re-call with identical arguments. Resolve it once and reuse the payload. Also call `forecast_confidence` (confidence, velocity, stage distribution).
8. **Capacity vs target** — `capacity_to_target_planner`, grouped by `team` and/or `sales_role`. Separates capacity-constrained territories (not enough reps) from execution-constrained ones (enough reps, target still at risk). Feeds Slide 3. Permission-gated.
9. **Reverse capacity** — `reverse_capacity_planner`, grouped the same way. Converts an Intervene territory's gap-to-target into a headcount estimate. Feeds Slide 9. Permission-gated.
10. **Renewal defence** — `renewal_forecast_summary`: ARR renewing in the next 30–180 days and at-risk renewal ARR, ideally by territory. Feeds Slide 4. Permission-gated.
11. **Ramp cohort** — `ramp_cohort`: reps still inside their ramp window. Use it before calling any territory "underperforming". Permission-gated; check the live schema for roster-level vs per-rep arguments and filter locally if it is roster-level.
12. **Hunter/farmer mix** — `hunter_farmer_mix`: new-business vs expansion mix per territory. Feeds Slide 6. Permission-gated; same schema check as `ramp_cohort`.
13. **Account health movement** — `account_health_movement`: accounts trending healthy → at-risk → critical (or back) per territory over the period. Feeds Slide 5. Permission-gated. Movement is **correlational**: accounts "moved" or "trended", never "a territory or rep caused".

### Handling missing data

Adapt; do not fail. A missing value is **unavailable**, never zero or healthy (preflight §5).

- No territory breakdown from `account_intelligence_summary` or `segment_performance_summary` → use the Step 1 fallback (explicit account attributes only) and disclose it.
- ARR growth with no territory breakdown → show the aggregate and label it company-wide.
- `activity_gaps` returns an empty list → report "No dormant accounts returned for the {days}-day window" and treat it as **indeterminate** unless the tool marks the empty result as verified. Never render it as "all territories engaged".
- A territory with zero accounts or zero pipeline **in the CRM** → absence of CRM records is not proof of whitespace. Flag it as a **coverage question to validate with market data** (addressable accounts, firmographic lists, external research), not as an opportunity.
- `capacity_to_target_planner`, `reverse_capacity_planner`, `renewal_forecast_summary`, `ramp_cohort`, `hunter_farmer_mix` and `account_health_movement` are manager/team-permission gated. If one is unauthorized or empty, drop only the enhancement it feeds (capacity badge, headcount estimate, renewal panel, ramp adjustment, hunter/farmer strip, movement view) and fall back as described per slide. Summarise gaps in the closing limits; never show raw permission errors.

## Step 3: Reconcile records to territories

Before computing any indicator:

1. Assign every account and opportunity to exactly one territory using the Step 1 basis.
2. Track **unassigned** records (no value in the territory attribute) and **ambiguously assigned** records (conflicting values, e.g. account region ≠ owner region, or multiple matches) **separately**. Never fold them into the nearest territory or drop them silently.
3. Report the count and value of unassigned/ambiguous records on Slide 2. If they exceed ~10% of accounts or pipeline value, say so in the headline limits: territory comparisons are partial.
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

### Coverage questions and expansion

Identify:

- Territories with little or no CRM revenue or pipeline → **coverage questions** to validate with market data. Absence of records is not evidence of untapped demand.
- Low account counts relative to an externally known market size (only when that market size comes from a cited source).
- Existing accounts with no active pipeline.
- Healthy accounts with no expansion motion underway (expansion candidates from `account_intelligence_summary`).

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

**Typography**: Georgia headers (36–44pt), Calibri body (14–16pt).
**Layout**: 16:9 widescreen, 0.5" minimum margins. Dark title/close slides, light content slides. If a demo label applies, put it on every slide.

### Slide structure (10 slides, ~25-minute review)

Adjust the composition when the number of territories or data density needs it; keep the content contract.

#### Slide 1: Title
- Navy background. "Territory Review", period label, date, organization name, "Powered by Summit53". Centered; large Georgia title, Calibri subtitle.

#### Slide 2: Territory overview
- Sources: `account_intelligence_summary` (`territory_summary`), `unified_forecast_summary`, optional `segment_performance_summary`.
- Four stat cards: territories active, accounts under management, pipeline value, aggregate ARR.
- Below: one row/card per territory (account count, pipeline, ARR, account-health mix). Left border colour comes from the server's health categories via `healthColor()`; slate when unavailable.
- Add a separate **Unassigned / ambiguous** row with its counts and value (Step 3).
- One-line basis note: "Territory basis: {basis}. {N} unassigned, {M} ambiguous records shown separately."

#### Slide 3: Territory scorecards
- Sources: `account_intelligence_summary`, `capacity_to_target_planner`, `ramp_cohort`.
- One card per territory (2×2 or 2×3): name, account count, pipeline, ARR, health mix (server categories), active deal count, and a **capacity verdict** badge — "On track to hit target", "Capacity-constrained" or "Execution-constrained". Omit the badge if the tool is unauthorized or empty; never guess.
- More than 6 territories → show the top 6 by ARR and state how many more exist.
- Before flagging a card red, check `ramp_cohort`. If a meaningful share of the territory's reps are ramping, note it on the card (e.g. "2 of 4 AEs ramping — judged against ramp plan"). Named reps only for authorized audiences.

#### Slide 4: Pipeline distribution by territory
- Sources: `unified_forecast_summary`, `forecast_confidence`, `pipeline_risk_summary`, `renewal_forecast_summary`.
- Bar chart (stacked by stage or risk level) of pipeline per territory, then a table: Territory | Pipeline | Target | Coverage ratio. Coverage colour via `coverageColor()`: below 2× red, 2–3× amber, 3×+ emerald; slate if target unavailable.
- **Deal-size composition**: mini-chart from `kpis.pipeline_coverage.by_deal_size`. If `acv_drift.is_significant` is `true`, add one amber line: "Pipeline ACV is drifting {direction} {drift_pct}% vs trailing-12-month closed-won — pipeline deals no longer resemble what the team has historically closed." Omit when not significant.
- **Renewal defence** panel from `renewal_forecast_summary`: ARR renewing in 30–180 days and at-risk renewal ARR per territory. If unavailable: "Renewal defence data unavailable — showing new pipeline only."

#### Slide 5: Account health by territory
- Sources: `account_health_movement` (primary), `account_intelligence_summary` `health_distribution` (snapshot/fallback).
- Lead with movement: accounts that trended healthy → at-risk and at-risk → critical per territory. Pair with the healthy / at-risk / critical distribution (counts and proportions). Below: top 5 at-risk accounts — Account, Territory, Health, ARR, Primary risk factor.
- Correlational language only. If movement is unavailable: "Health movement unavailable — showing point-in-time snapshot."
- Answers: "Where are accounts most vulnerable, and which territories are trending the wrong way?"

#### Slide 6: Coverage questions and expansion
- Sources: synthesis of all pulls; `hunter_farmer_mix` for deal-mix enrichment.
- Two columns:
  - **Left — "Coverage questions to validate"** (navy accent): territories or segments with little or no CRM revenue/pipeline, with what the CRM does show (accounts with no deals, large accounts with no engagement) and the market evidence needed to confirm real whitespace. Never title this column "untapped" or "whitespace" unless external market evidence is cited.
  - **Right — "Expansion opportunities"** (emerald accent): healthy existing accounts with room to grow, from `account_intelligence_summary` expansion candidates.
- **Hunter/farmer strip** beneath: new-business vs expansion split per territory, to show whether flat growth is a hunting or farming pattern. Drop the strip if unavailable.

#### Slide 7: Engagement gaps by territory
- Source: `activity_gaps`.
- If dormant accounts were returned: amber callout with count and ARR attached, then a table grouped by territory (Account, Territory, Days since last activity, ARR). Highlight the territories with the most dormant accounts.
- If the list is empty: a **neutral** (slate) note — "No dormant accounts returned for the {days}-day window." Do not use a green "all engaged" callout; no logged activity and no returned gap are both indeterminate without a verified-zero flag.

#### Slide 8: Deal health by territory
- Sources: `risk_heatmap`, `pipeline_risk_summary`.
- Table of the least healthy deals, annotated by territory: Deal, Territory, Amount, Stage, Health score, Health band, Top risk factor. Colour from the server's `healthBand` via `healthBandColor()`: `Low` → red, `Medium` → amber, `High` → emerald, missing → slate "band unavailable". Order by `healthScore` ascending. Cap at 10 rows; navy header row, white text.
- Callout: which territory carries the most `Low`-band deal value (with count and denominator).

#### Slide 9: Territory recommendations
- Sources: Step 4 recommendations; `reverse_capacity_planner` for Intervene items.
- 3–5 numbered recommendations (emerald numbered circles), each with a bold action headline, one supporting sentence (evidence with denominators, expected outcome), and a tag: **Evidence-backed** or **Hypothesis to validate**.
- Group as **Double down** (performing territories), **Intervene** (needing attention), **Explore** (coverage questions; these are hypotheses by default).
- For each Intervene item, translate the gap into a headcount estimate where `reverse_capacity_planner` is available (e.g. "West: ~1.4 additional AEs estimated to reach target"). Otherwise use qualitative effort-shift language. No reassignment advice from raw pipeline alone.

#### Slide 10: Close — basis, sources and limits
- Navy background. Title: "Territory Strategy: Where We Play, How We Win", organization name, date.
- Lower block (Ice Blue text): territory basis, period and currency, unassigned/ambiguous counts, sources used, sources unavailable (summarised, no raw errors), and the demo label if it applies.

## Step 6: Generate the file

Write one Node.js PptxGenJS script that:

1. Embeds all pulled and calculated data directly (no external data files).
2. Uses factory functions for shadows and option objects (PptxGenJS mutates option objects; never reuse them across calls).
3. Defines helpers: `addStatCard()`, `addSectionTitle()`, `healthBandColor()`, `healthColor()`, `coverageColor()`, `formatCurrency()`, `territoryCard()`.
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

// Currency resolved in Step 1; null renders as "unavailable", never $0.
function formatCurrency(val, symbol = "$") {
  if (val == null || Number.isNaN(val)) return "unavailable";
  if (Math.abs(val) >= 1e6) return `${symbol}${(val / 1e6).toFixed(1)}M`;
  if (Math.abs(val) >= 1e3) return `${symbol}${(val / 1e3).toFixed(0)}K`;
  return `${symbol}${val}`;
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
- **Make Intervene asks concrete** — a headcount estimate beats a vague effort shift — and keep hypotheses labelled as hypotheses.
- **Keep it to 10 slides.**

## Verification checklist

- [ ] Preflight checklist complete; `scoped_org_id` matched on returned data
- [ ] Territory basis stated; derived groupings disclosed
- [ ] Unassigned and ambiguous records counted separately
- [ ] Comparisons normalised; denominators shown
- [ ] Deal colours follow server `healthBand`; no raw-threshold or inverted colouring
- [ ] No "whitespace" claim from absent CRM records; empty `activity_gaps` not shown as green
- [ ] Every recommendation tagged evidence-backed or hypothesis; no reassignment from raw pipeline alone
- [ ] Rep-level detail only for an authorized audience
- [ ] Demo label applied if fixtures could not be excluded
- [ ] Every slide rendered and inspected; one link returned
