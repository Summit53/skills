# Signal Catalog — revenue-action-brief-s53

The authoritative registry for the Revenue Action Brief. Each signal defines: what fires it, the decay profile that places it on a horizon, what scales its severity, and how to phrase the recommendation.

## Contents

- [Domain A — Deal-level execution](#domain-a--deal-level-execution)
- [Domain B — Rep / team execution](#domain-b--rep--team-execution)
- [Domain C — Pipeline shape & forecast](#domain-c--pipeline-shape--forecast)
- [Domain D — Retention & structural](#domain-d--retention--structural)
- [Domain E — Pipeline generation (target accounts, optional)](#domain-e--pipeline-generation-target-accounts-optional)
- [Maintenance notes](#maintenance-notes)

**How to read a signal block:**

- **source** — MCP tool(s) and field path(s) the detection rule reads.
- **detection** — the condition that fires the signal.
- **U (urgency decay)** — latest responsible moment to act. `dynamic` means recompute from context.
- **R (action runway)** — minimum time for the fix to be set up and start working.
- **horizon** — computed by the rule (slowest bucket B where B ≤ U and B ≥ R). The value shown is the default; dynamic-U signals may land elsewhere, and any signal where R > U at detection time moves to the **Already Behind** lane.
- **trend** — `level` (single reading) or `trend` (needs change data; degrade gracefully to level if absent).
- **severity** — what scales this signal's ranking *within its horizon*.
- **prescription / evidence** — templates; `{…}` are placeholders filled from the data.
- **money placeholders** (`{amount}`, `{pipeline_value}`, `{quota}`, `{at_risk_value}`, `{churned_arr}`, `{revenue_per_rep}`, …) are written with the reporting currency's ISO code or unambiguous symbol read from the response's `metadata.currency` (`NZ$689K`, `€1.2M`) — never a bare `$` unless the reporting currency is USD. When a total excludes unconverted amounts, the evidence line says so. See [currency-and-fx.md](currency-and-fx.md).

Horizon scale: today ≤1d · week ≤7d · month ≤30d · quarter ≤90d.

---

## Domain A — Deal-level execution

### A1 · deal_dark_closing
- **source**: `risk_heatmap` (`lastActivity`, `closeDate`, `forecastCategory`, `amount`); cross-check `team_action_plan` opportunities
- **detection**: last activity > 14 days AND close date < 7 days away AND forecast category in {Commit, Best Case}
- **U**: dynamic — 1d when close date < 7d; tightens to same-day as close date approaches
- **R**: 1d (a direct re-engagement touch)
- **horizon**: today
- **trend**: level
- **severity**: amount × forecast category weight (Commit > Best Case)
- **prescription**: "Re-engage {deal} — {owner} to make direct contact today (call, not email)."
- **evidence**: "{amount} {forecast_category}, {N} days since last activity, closes {close_date}."

### A2 · deal_overdue_close
- **source**: `team_action_plan` opportunities / `risk_heatmap` (`closeDate`, `stage`, `amount`)
- **detection**: close date is in the past AND deal still open
- **U**: 1d (forecast integrity degrades every day it sits)
- **R**: 1d (push the date with a reason, or disposition the deal)
- **horizon**: today
- **trend**: level
- **severity**: amount
- **prescription**: "Disposition {deal} — its close date has passed; {owner} to either re-date it with a documented reason or move it to Closed Lost."
- **evidence**: "Close date {close_date}, {N} days overdue; {amount}; stage {stage}."

### A3 · deal_dark_active
- **source**: `risk_heatmap` (`lastActivity`, `closeDate`, `amount`); `team_action_plan` (`is_strategic`)
- **detection**: last activity > 14 days AND close date > 7 days away
- **U**: 1w
- **R**: 1d
- **horizon**: this week
- **trend**: level
- **severity**: amount, weighted up if `is_strategic`
- **prescription**: "Schedule a touch on {deal} this week — {owner} to re-establish contact."
- **evidence**: "{amount}, {N} days since last activity, closes {close_date}."

### A4 · framework_gap_late_stage
- **source**: `risk_heatmap` (`stage`, `frameworks.meddpicScore`, `amount`)
- **detection**: stage in {Negotiation, Proposal} AND `meddpicScore` < 0.5
- **U**: 1w
- **R**: 1w (a discovery touch plus internal review)
- **horizon**: this week
- **trend**: level
- **severity**: amount
- **prescription**: "Strengthen qualification on {deal} before it advances — its MEDDPIC score is {meddpicScore} in {stage}; {owner} to run a discovery touch closing the weakest elements."
- **evidence**: "Stage {stage}, MEDDPIC score {meddpicScore}; {amount}."
- **note**: `risk_heatmap` exposes only the composite `meddpicScore`, not element-level scores — detection uses the composite. Do **not** use `meddpicCompletion` (observed 1.0 across all deals — it does not discriminate) or `threeWhysCompletion` (observed 0.0 across all deals — unpopulated). To name the specific weak element (Economic Buyer, Champion, Decision Process) in the prescription, optionally call `opportunity_framework_summary` for the flagged deal as an enrichment step; if not called, speak to the composite gap.

### A5 · high_value_deal_low_health
- **source**: `risk_heatmap` (`amount`, `healthScore`, deal-size band)
- **detection**: deal in the top deal-size band AND health score < 0.45
- **U**: 1w
- **R**: 1w (a structured deal review)
- **horizon**: this week
- **trend**: level
- **severity**: amount
- **prescription**: "Run a deal review on {deal} this week — a deal this size at this risk level warrants structured inspection by you and {owner}."
- **evidence**: "{amount}, health score {health}, stage {stage}."

### A6 · stage_regression
- **source**: `risk_heatmap` stage vs prior reading (trend — requires a prior snapshot)
- **detection**: deal moved backward a stage since the last reading
- **U**: 1w
- **R**: 1d
- **horizon**: this week
- **trend**: trend — if no prior reading is available, this signal does not fire (no graceful level fallback exists)
- **severity**: amount
- **prescription**: "Inspect {deal} — it regressed from {stage_prev} to {stage_now}; {owner} to identify what changed before the next pipeline review."
- **evidence**: "Stage moved {stage_prev} → {stage_now}; {amount}."

### A7 · close_date_pushed
- **source**: `risk_heatmap` (`closeDateMoved`, `closeDate`, `stage`, `amount`)
- **detection**: `closeDateMoved` = 1 (the deal's close date has changed)
- **U**: 1w
- **R**: 1d (re-confirm the date and the step gating it)
- **horizon**: this week
- **trend**: level — `closeDateMoved` is supplied directly per deal, so this fires on a single reading with no prior snapshot. It is the level-data complement to A6: A6 catches stage slippage (snapshot-dependent), A7 catches date slippage (always available).
- **severity**: amount
- **prescription**: "Pressure-test the timeline on {deal} — its close date has moved; {owner} to re-confirm whether the new date is realistic and what step is gating it."
- **evidence**: "Close date moved; {amount}, stage {stage}, now closes {close_date}."

---

## Domain B — Rep / team execution

### B1 · owner_priority_backlog
- **source**: `weekly_action_plan` (`urgency_level`, `priority_score`, `status`, `suggested_action`)
- **detection**: one or more items with urgency = high AND priority_score > 80 AND status in {pending, snoozed}
- **U**: 1w
- **R**: ≤1w
- **horizon**: this week — escalates to **today** for any item with priority_score > 90
- **trend**: level
- **severity**: priority_score
- **prescription**: "Clear your own high-priority items — {N} task(s) scored {priority_score}+ are still open, including: {suggested_action}."
- **evidence**: "{N} open items above priority 80; highest is {priority_score}."

### B2 · rep_low_completion
- **source**: `team_action_plan` (`members[].completion_rate`, `summary.avg_completion_rate`)
- **detection**: a rep's completion rate is more than 25 percentage points below the team average
- **U**: 1w (the next 1:1)
- **R**: 1w (a coaching conversation)
- **horizon**: this week
- **trend**: level
- **severity**: completion gap × rep's total pipeline value
- **prescription**: "Coach {rep} this week — use the 1:1 to diagnose whether the gap is capacity, prioritisation, or disengagement."
- **evidence**: "Action completion {rate}% vs team average {avg}%."

### B3 · rep_snoozed_priority_deal
- **source**: `team_action_plan` (`members[].flagged_deals` with `status` = snoozed)
- **detection**: a rep has a high-priority flagged deal whose action is snoozed
- **U**: 1w
- **R**: 1w
- **horizon**: this week
- **trend**: level
- **severity**: deal amount
- **prescription**: "Ask {rep} about {deal} — a flagged action ({suggested_action}) has been snoozed; a snoozed flagged deal usually signals a hidden blocker."
- **evidence**: "Flagged action '{suggested_action}' snoozed on a {amount} deal."

### B4 · team_completion_decay
- **source**: `team_action_plan` (`summary.avg_completion_rate`)
- **detection**: team average completion rate < 50%
- **U**: 1m
- **R**: 2–4w (a cadence or review-rhythm change takes weeks to bed in)
- **horizon**: this month
- **trend**: level
- **severity**: distance below 50%
- **prescription**: "Address team execution discipline this month — tighten the action cadence or review rhythm; this is a process signal, not an individual one."
- **evidence**: "Team average action completion {rate}% across {N} reps."

### B5 · rep_capacity_imbalance
- **source**: `unified_forecast_summary` (`detailed_outliers.rep_concentration`)
- **detection**: pipeline concentration high — single-rep share above ~30%, or a high Gini coefficient
- **U**: 1m
- **R**: 1m (redistribution or coverage planning)
- **horizon**: this month
- **trend**: level
- **severity**: single-rep concentration %
- **prescription**: "Rebalance pipeline load this month — {rep} carries {pct}% of total pipeline; plan redistribution or coverage to reduce single-rep forecast risk."
- **evidence**: "{rep} holds {pct}% of pipeline; concentration level {level}."

---

## Domain C — Pipeline shape & forecast

### C1 · acv_drift_significant
- **source**: `unified_forecast_summary` (`kpis.pipeline_coverage.acv_drift`)
- **detection**: `acv_drift.is_significant` = true
- **U**: 2–3w
- **R**: 1w (a pipeline review plus a qualification-criteria adjustment)
- **horizon**: this week
- **trend**: level (the field is self-contained; never gate on its presence — always gate on `is_significant`)
- **severity**: `drift_pct` magnitude
- **prescription**: "Review pipeline qualification with the team — average deal size is drifting {direction} {drift_pct}% versus your trailing-12-month closed-won average; pressure-test the outlier deals."
- **evidence**: "Pipeline ACV {current_avg} vs historical {historical_avg}, {direction} {drift_pct}%."

### C2 · close_date_clustering
- **source**: `unified_forecast_summary` (`detailed_outliers.close_date_clustering`)
- **detection**: month-end or quarter-end cluster exceeds 35% of deal value
- **U**: 1–2w (clean before period-end)
- **R**: 1w (a close-date audit with reps)
- **horizon**: this week
- **trend**: level
- **severity**: clustered value ($) — the dollar amount of pipeline sitting in the period-end cluster
- **prescription**: "Audit close dates with the team this week — run a realism pass before the period-end cluster inflates the forecast."
- **evidence**: "{pct}% of pipeline value clustered at period-end ({deal_count} deals)."

### C3 · revenue_at_risk_spike
- **source**: `unified_forecast_summary` (`revenue_at_risk`)
- **detection**: revenue at risk > 25% of pipeline
- **U**: dynamic — 1w when the at-risk value is concentrated in near-close deals, otherwise 1m
- **R**: 1w
- **horizon**: this week or this month, depending on U
- **trend**: level
- **severity**: at-risk dollar value
- **prescription**: "Triage revenue at risk — {pct}% of pipeline ({amount}) is flagged across {N} deals; work the near-close deals first."
- **evidence**: "{amount} at risk, {pct}% of pipeline, {N} deals; primary cause {primary_risk_type}."

### C4 · coverage_below_target
- **source**: `unified_forecast_summary` (`kpis.pipeline_coverage.ratio`)
- **detection**: pipeline coverage ratio < 2.5x
- **U**: dynamic — 1m with most of the quarter remaining; tightens to 1w as the quarter runs out
- **R**: 2–4w (prospecting takes weeks to land)
- **horizon**: this month — moves to **Already Behind** when U has tightened below R late in the quarter
- **trend**: level
- **severity**: gap to the 3x target
- **prescription**: "Build pipeline this month — coverage is {ratio}x against a 3x target; prospecting needs to start now to protect next quarter."
- **evidence**: "Coverage {ratio}x; pipeline {pipeline_value} against {quota} quota."

### C5 · lead_velocity_negative
- **source**: `unified_forecast_summary` (`kpis.lead_velocity_rate`)
- **detection**: lead velocity rate strongly negative (pipeline shrinking month-over-month)
- **U**: 1m
- **R**: 1m (a demand-gen ramp)
- **horizon**: this month
- **trend**: trend — `lead_velocity_rate` is supplied directly by the tool, so this fires as a level read
- **severity**: rate magnitude
- **prescription**: "Address top-of-funnel this month — pipeline is shrinking; re-examine demand-gen and prospecting output."
- **evidence**: "Lead velocity {rate}%, trend {trend}."

### C6 · win_rate_band_weak
- **source**: `unified_forecast_summary` (`kpis.win_rate.by_deal_size`)
- **detection**: one deal-size band's win rate is materially below the others
- **U**: 1m
- **R**: 2–4w (process diagnosis plus coaching)
- **horizon**: this month
- **trend**: level
- **severity**: the weak band's pipeline exposure
- **prescription**: "Diagnose the {band} segment this month — a blended win rate is hiding it; decide between coaching, a higher qualification bar, or pricing."
- **evidence**: "Win rate {band_rate}% in the {band} band vs {other_rate}% elsewhere."

### C7 · account_concentration
- **source**: `unified_forecast_summary` (`detailed_outliers.account_concentration`)
- **detection**: a single account exceeds 25% of pipeline
- **U**: 1q
- **R**: 1q (diversification is structural)
- **horizon**: this quarter
- **trend**: level
- **severity**: concentration %
- **prescription**: "Plan account diversification this quarter — build a structural plan to reduce dependence on {account}."
- **evidence**: "{account} is {pct}% of pipeline ({amount})."

### C8 · pipeline_stall_load
- **source**: `deal_drag_summary` (`avg_waste_score`, `medium_risk_count`, `medium_risk_value`, `high_risk_count`, `high_risk_value`, `most_affected_stage`); `deal_drag_dashboard` for per-deal detail (optional enrichment)
- **detection**: (`medium_risk_count` + `high_risk_count`) ≥ 5, OR (`medium_risk_value` + `high_risk_value`) > 10% of total pipeline value
- **U**: 1–2w (a stalled deal left another week hardens toward dead)
- **R**: 1w (a stalled-deal review with deal owners)
- **horizon**: this week
- **trend**: level
- **severity**: at-risk waste value ($) = `medium_risk_value` + `high_risk_value` — the dollar-exposure common denominator
- **prescription**: "Run a stalled-deal review this week — {risk_deal_count} deals ({at_risk_value}) are accumulating drag (avg waste score {avg_waste_score}, worst concentrated in {most_affected_stage}); work the highest-waste deals with their owners and decide re-engage or disqualify."
- **evidence**: "{risk_deal_count} deals at medium-or-high drag risk; {at_risk_value} of pipeline carrying drag; avg waste score {avg_waste_score}."
- **note**: `deal_drag` scopes all open opportunities, not just the current-period pipeline — its deal count is therefore wider than `unified_forecast_summary`'s active count. This is by design for a drag analysis (a deal stalling is wasteful regardless of its close quarter), not a discrepancy. For per-deal drill-down — worst-waste deals, drag cause (`by_cause`), drag scenario (`zombie_deals`, `approval_bottlenecks`, `feature_creep`), and `priority_interventions` with recommended actions — call `deal_drag_dashboard` as an enrichment step; those recovery actions feed the Step 7 handoff.

---

## Domain D — Retention & structural

### D1 · logo_churn_elevated
- **source**: `arr_growth_analytics` (`logo_churn`)
- **detection**: logo churn rate above threshold or rising
- **U**: 1m
- **R**: 1m (a customer-success intervention)
- **horizon**: this month
- **trend**: trend — degrade to level on the rate if no change data
- **severity**: churn rate × ARR exposure
- **prescription**: "Investigate logo churn this month — pull the churn reasons and tighten the at-risk renewal playbook."
- **evidence**: "Logo churn {rate}% — {churned_logos} of {total_renewal_logos} renewal accounts lost."

### D2 · ttv_lengthening
- **source**: `arr_growth_analytics` (`time_to_value`)
- **detection**: median time-to-value above threshold or rising
- **U**: 1m
- **R**: 1m (an onboarding-process change)
- **horizon**: this month
- **trend**: trend — degrade to level on the median if no change data
- **severity**: change versus prior, or distance above threshold
- **prescription**: "Examine onboarding velocity this month — slow time-to-value erodes retention; review the onboarding path."
- **evidence**: "Median time-to-value {median_days} days (p75 {p75_days}), {contracts_measured} contracts measured."

### D3 · grr_erosion
- **source**: `arr_growth_analytics` (`grr`)
- **detection**: GRR below 85–90%, or declining
- **U**: 1q
- **R**: 1q (sustained onboarding and CS investment)
- **horizon**: this quarter
- **trend**: trend — degrade to level on the GRR value if no change data
- **severity**: distance below the 90% target
- **prescription**: "Make gross retention a quarter priority — this is structural; it needs sustained onboarding and CS investment, not a single fix."
- **evidence**: "GRR {grr}%, below a healthy 90%; churned ARR {churned_arr} against renewal base {renewal_base}."

### D4 · nrr_below_threshold
- **source**: `arr_growth_analytics` (`nrr`)
- **detection**: NRR below 100%, or dropping
- **U**: 1q
- **R**: 1q
- **horizon**: this quarter
- **trend**: trend — degrade to level on the NRR value if no change data
- **severity**: **always ranks first in its horizon when it fires** (severity override)
- **prescription**: "Treat net retention as the quarter's top structural priority — expansion is no longer offsetting churn; the retention motion needs investment."
- **evidence**: "NRR {nrr}%, below the 100% line; tier {tier}."

### D5 · revenue_per_rep_low
- **source**: `unified_forecast_summary` (`team_summary.revenue_per_rep`)
- **detection**: revenue per rep below benchmark, or declining
- **U**: 1q
- **R**: 1q (enablement, ramp, or capacity change)
- **horizon**: this quarter
- **trend**: trend — degrade to level if no change data
- **severity**: gap to benchmark
- **prescription**: "Review per-rep productivity this quarter — decide whether the gap is enablement, ramp, or capacity."
- **evidence**: "Revenue per rep {revenue_per_rep} across {quota_carrying_reps} quota-carrying reps."

### D6 · arr_mix_stage_misalignment
- **source**: `arr_growth_analytics` (`arr_mix`, `gap_to_target`, `arr_band`)
- **detection**: revenue mix is off-benchmark for the company's ARR band — a `gap_to_target` engine delta beyond tolerance
- **U**: multi-quarter
- **R**: 1q
- **horizon**: this quarter (capped at the longest bucket)
- **trend**: level
- **severity**: the largest engine gap
- **prescription**: "Rebalance the revenue engines this quarter — shift GTM investment to close the {engine} gap for your growth stage."
- **evidence**: "{engine} mix {current_pct}% against a {target_pct}% benchmark for the {arr_band} stage."

---

## Domain E — Pipeline generation (target accounts, optional)

Source: `target_account_funnel_summary` (default `weeks: 6`). Requires the customer's Outreach plan — if the capability is not exposed or is access-denied, these signals are **not assessed** (one "Not assessed" entry); if it returns `total_accounts: 0`, the customer does not run target accounts and nothing fires, with no note. Target-account rows carry no dollar exposure: in a mixed horizon they rank **below** items with dollar exposure (Step 5), and each signal collapses its accounts into **one** recommendation naming at most three accounts plus "+ N more". Account is the collapse key across E1 and E3 — merge into the faster horizon. Read-only: never create, update or convert a target account, and never submit, accept or dismiss stakeholder suggestions from this brief.

### E1 · target_account_stalled
- **source**: `target_account_funnel_summary` (`stalled_accounts[]` — `name`, `stage`, `days_in_stage`, `gaps`, `stuck.hint`, `stuck.action`; `settings.stall_after_days`)
- **detection**: `stalled_accounts` is non-empty (the server has already applied `days_in_stage` > `settings.stall_after_days` to active accounts — do not re-threshold)
- **U**: 1w (an account left another week in the same stage cools toward nurture)
- **R**: 1d (the `stuck.action` is a single step: write the thesis, open the next lead, widen, or open the account)
- **horizon**: this week
- **trend**: level
- **severity**: later stage first (`meeting_booked` > `engaging` > `researching` > `identified`), then `days_in_stage` − `stall_after_days`
- **prescription**: "Unstick {N} target account(s) this week — {account}: {stuck.hint}, next step {stuck.action as plain words}; {more accounts}."
- **evidence**: "{account} {days_in_stage} days in {stage} against a {stall_after_days}-day stall threshold; committee gaps {gaps}."
- **note**: render `stuck.action` in plain words — `write_thesis` → "write the account thesis", `open_lead` → "open the next thread", `widen` → "widen the committee", `open_account` → "review the account". Quote `stuck.hint` verbatim.

### E2 · touch_target_behind
- **source**: `target_account_funnel_summary` (`this_week.touches`, `this_week.target`, `this_week.remaining`, `this_week.per_day[]`, `this_week.average_previous_4_weeks`, `this_week.untouched_accounts[]`)
- **detection**: `this_week.target` > 0 AND `touches` < 0.75 × (`target` × working days elapsed ÷ 5), counting working days from `per_day[]`; on the last working day, any `remaining` > 0
- **U**: 1w (the weekly target resets at `week_start` + 7 days)
- **R**: 1d (a prospecting block)
- **horizon**: this week
- **trend**: level — add "versus a {average_previous_4_weeks} weekly average" when that field is non-null
- **severity**: `remaining` touches, then the count of `untouched_accounts`
- **prescription**: "Book prospecting time this week — {touches} of {target} target-account touches done with {remaining} to go; start with untouched accounts that already have a thesis ({accounts})."
- **evidence**: "{touches}/{target} touches week of {week_start}; {N} target accounts untouched this week."
- **note**: prefer `untouched_accounts` with `has_thesis: true` and `touch_allowed_now: true` when naming accounts. Does not fire when `settings.weekly_touch_target` is null or 0.

### E3 · widen_committee_gaps
- **source**: `target_account_funnel_summary` (`widen_next[]` — multithreaded accounts with an engaged champion and committee gaps, each with `up_next` and `gaps`)
- **detection**: `widen_next` is non-empty
- **U**: 1m (an engaged champion without a wider committee stalls at the first budget or technical question)
- **R**: 1w (map the missing roles and open the next thread)
- **horizon**: this month
- **trend**: level
- **severity**: later stage first, then number of `gaps` (economic buyer gap weighs highest)
- **prescription**: "Widen the buying committee on {account} this month — champion engaged, still missing {gaps}; next thread is the {up_next.committee_role}."
- **evidence**: "{account}: champion engaged, gaps {gaps}, coverage {coverage_pct}%; next thread {up_next.committee_role}."
- **note**: single-threaded accounts have `coverage_pct: null` — write "coverage not applicable", never 0%. For the full committee, `get_target_account` or `get_stakeholder_research_brief` (read-only) may enrich the item when the leader asks.

---

## Maintenance notes

- **Thresholds are deliberately conservative.** Tune the numeric cutoffs (the 25% concentration, the 0.45 health floor, the 50% completion floor, the GRR 90% target) per deployment if a customer's benchmarks differ.
- **U and R drive everything.** Changing a signal's horizon is done by editing its U/R values here — never by hardcoding a horizon in the skill logic.
- **Adding a signal** means adding a full block here with all fields. The skill will not horizon-assign a signal that lacks a U/R pair.
- **FX is never a signal.** For trend reads on ARR-derived signals (Domain D), when `arr_growth_analytics.constant_currency.status` is `partial` or `complete` and `fx_effect` is material, judge "declining" or "rising" on the constant-currency `delta`, not the reported `actual_delta`, and name the FX effect in the evidence line. Currency movement alone never fires D1–D6.
- **Domain E thresholds come from the customer's own settings** (`stall_after_days`, `weekly_touch_target`). The only local constant is E2's 0.75 pro-rata tolerance — tune it per deployment.
- **`acv_drift`** is gated on `is_significant`, never on field presence — the field is always an object even when drift is sub-threshold.
- **Unreliable `risk_heatmap` fields — do not build signals on these.** `meddpicCompletion` was observed at 1.0 across every deal (does not discriminate) and `threeWhysCompletion` at 0.0 across every deal (unpopulated). Use `meddpicScore` for MEDDPIC strength. Re-test these fields before relying on them; if a future backend fix populates them meaningfully, the catalog can adopt them.
- **`risk_heatmap` exposes only composite framework scores**, not element-level MEDDPIC. Element-level detail (which of Economic Buyer / Champion / Decision Process is weak) requires `opportunity_framework_summary` per deal — used as optional enrichment, not detection.
