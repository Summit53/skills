---
name: "revenue-action-brief-s53"
description: "Generate a prioritized, read-only revenue action brief for a VP Sales or CRO, organized into today, this week, this month, and this quarter. Use live Summit53 CRM evidence to answer what needs attention, what to focus on, where to spend time, or what the leader should do next. Keep this customer-facing and separate from Summit53's internal GTM workflows. Do not use for weekly forecast movement ('why did the number move') — use forecast-delta-brief. Do not use to draft emails or write CRM records — the brief only hands off to a write-capable skill after the user explicitly asks for and approves that action."
metadata:
  version: "1.2.0"
  baselined: "2026-10-13"
  status: "active"
---

# Revenue Action Brief

Produce a horizoned action brief for a sales leader: exactly what to do **today**, **this week**, **this month**, and **this quarter** — every recommendation evidence-cited from live CRM data and placed in the horizon that matches how fast its underlying signal decays. It reads like a diagnosis with a prognosis, not a flat to-do list.

## Route first

- Weekly forecast movement ("why did the number move this week") → `forecast-delta-brief`.
- Drafting emails, re-engagement touches, coaching materials or CRM writes → not this skill. The brief may hand an item to a write-capable skill only after the leader explicitly asks for and approves that action (Step 7).
- Prioritizing what to do today, this week, this month or this quarter stays here.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its checklist before any data call.

Skill-specific gates:

- **Preflight every read capability** this skill uses before the first data call: the eight data reads in Step 2 (`unified_forecast_summary`, `arr_growth_analytics`, `risk_heatmap`, `deal_drag_summary`, `forecast_confidence`, `team_action_plan`, `weekly_action_plan`, `activity_gaps`) plus `get_job` for the async flow, `deal_drag_dashboard` if a C8 handoff is requested, and the **optional** `target_account_funnel_summary` (pipeline-generation signals; requires the customer's Outreach plan — if it is not exposed or is access-denied, Domain E is not assessed and the brief continues). If they are deferred, load them all in one batch ([host-adapters.md](references/host-adapters.md#loading-the-summit53-tools)), then inspect each live schema. Tool names and arguments in this file are semantic guidance; follow the live schema when it differs and note the difference.
- **Missing source ≠ zero.** If a capability is not exposed, errors, or is access-denied, record a missing-source note for it and suppress **only** the signals whose `source` depends on it (per the catalog). Never substitute zero, never treat the silence as health, and never let a missing source make the brief look calmer than the data supports.
- **Demo label.** Commercial artifact: if fixture rows cannot be separated, put **Demo data — not for customer or commercial decisions** under the brief's header.
- **Read-only.** No `refresh: true`. The brief never drafts, sends, logs, or writes. Handoffs follow Step 7.

References:

- [references/signal-catalog.md](references/signal-catalog.md) — read in full before Step 3; the authoritative signal registry.
- [references/async-envelopes.md](references/async-envelopes.md) — read before calling `unified_forecast_summary`; governs `get_job` polling and the identical-arguments re-call.
- [references/connector-preflight.md](references/connector-preflight.md) — the shared tenant, schema, fixture, read-only, missing-evidence and delivery contract.
- [references/currency-and-fx.md](references/currency-and-fx.md) — read before rendering any amount: reporting-currency labels, disclosure of excluded or unconverted amounts, constant currency, and why FX effect is never performance.
- [references/host-adapters.md](references/host-adapters.md) — how to load tools, save and deliver files, and refer to other skills on the current host.

## Why This Exists

Sales leaders are flooded with dashboards but starved of *sequencing*. Everything looks important; nothing tells them what is genuinely urgent versus what is structural. The result is either firefighting (only ever doing today's emergencies) or analysis paralysis (staring at quarter-level metrics with no daily handle).

This skill resolves that by separating two things every recommendation has: how soon the window to act closes, and how long the fix takes to work. A deal going dark is a today problem. ACV drift is a this-month pattern. Gross-retention erosion is a this-quarter structural signal. Same data platform, four different clocks.

## Boundary — This Is a Customer-Facing Skill

This skill is used by Summit53 **customers** — VP Sales and CROs running real teams. It is self-contained and generic. It must **not** read any internal Summit53 strategy, positioning, or accountability skill, and must not reference Summit53's own go-to-market. Its only inputs are the customer's own CRM data (via the MCP tools below) and the bundled references ([references/signal-catalog.md](references/signal-catalog.md), [references/async-envelopes.md](references/async-envelopes.md), [references/connector-preflight.md](references/connector-preflight.md), [references/currency-and-fx.md](references/currency-and-fx.md)). Keep all language vendor-neutral and applicable to any mid-market B2B sales org.

## How It Works

1. **Scope** — determine which horizon(s) the leader wants.
2. **Pull** — call the Summit53 MCP tools and capture raw responses.
3. **Detect** — match the data against the signal catalog.
4. **Assign horizons** — score each fired signal on urgency decay and action runway; compute its horizon.
5. **Rank and cap** — order each horizon by severity; cap to keep the brief scannable.
6. **Render** — write the brief.
7. **Hand off (optional)** — if the leader wants to act on an item, route it to the execution skill that owns that work.

## Step 1: Scope

Default to the **full four-horizon brief**. If the leader names a horizon ("what do I do today", "this quarter"), produce only that section but still run full detection underneath — a today-only request still needs the week/month/quarter signals computed so nothing that has decayed *into* today is missed.

Horizon scope values: `all` (default), `today`, `week`, `month`, `quarter`.

No other scoping questions. This skill is meant to be answered fast — do not interrogate the leader before producing the brief.

## Step 2: Pull Live Data

Call these Summit53 MCP tools. Launch in parallel — they are independent. Capture each raw response; detection in Step 3 reads specific fields.

| Tool | Why | Notes |
|------|-----|-------|
| `unified_forecast_summary` | Forecast confidence, coverage, revenue at risk, team metrics, deal-size segmentation, ACV drift | `detail_level: "detailed"` — **returns asynchronously, see below** |
| `arr_growth_analytics` | NRR, GRR, logo churn, time-to-value, ARR mix, growth stage | `include_changes: true`, `include_benchmarks: true` |
| `risk_heatmap` | Deal-level risk scores, MEDDPIC score, last activity, close-date movement | `page_size: 100`; **paginate until all `total` rows are retrieved** |
| `deal_drag_summary` | Stalled-deal load — waste scores, drag-risk distribution, most-affected stage | C8 source; `deal_drag_dashboard` is an optional per-deal enrichment call |
| `forecast_confidence` | Per-rep confidence, velocity issues | — |
| `team_action_plan` | Per-rep completion rate, flagged deals, deal close dates | Primary source for rep + deal-level signals |
| `weekly_action_plan` | The leader's own open high-priority tasks | `ai_generated` items may lack deal linkage — handle gracefully |
| `activity_gaps` | Dormant accounts | `days: 14` |
| `target_account_funnel_summary` | **Optional** — target-account pipeline generation: stalled accounts, weekly touches vs target, committee gaps to widen | Domain E source; requires the Outreach plan. Default `weeks: 6`. Never call target-account or stakeholder write tools |

From `unified_forecast_summary`, also capture `projected_landing` (`value`, `basis`, `fallback_reason`, `floored_to_closed_won`) and `metadata.currency`; from `arr_growth_analytics`, capture `constant_currency` (`status`, `delta`, `actual_delta`, `fx_effect`, `label`) and `metadata.currency`.

**`unified_forecast_summary` returns asynchronously.** The first call often returns a *processing envelope* — `{"status": "processing", "job_id": ..., "retry_after": N}` — instead of data. This envelope is **not** data; running detection against it will silently find nothing. Follow [references/async-envelopes.md](references/async-envelopes.md): poll `get_job` on the returned `job_id` until terminal, then **re-call `unified_forecast_summary` with identical arguments** to collect the payload. `get_job` returns lifecycle state, not the forecast. Budget 6 polls and 2 payload re-calls; stop immediately on `failed` or `cancelled`. If no payload arrives, treat the source as missing and carry the helper's note into the brief verbatim. Fire the other tools first so polling overlaps their execution.

**`risk_heatmap` paginates.** A mid-market pipeline commonly exceeds one page. Read the `total` field on the first response and page until every row is retrieved — an undersized pull makes the per-horizon caps and "+N more" counts wrong, even if the missing low-risk tail rarely adds today/week items.

If a tool errors, is not exposed, is access-denied, or returns no payload, do not fail. Record a **missing-source note** for it (which capability, and a plain-language reason — no raw errors), suppress only the catalog signals whose `source` depends on it, and run detection on everything else. A suppressed signal is **not assessed**, which is different from "did not fire": never substitute zero for the missing values, and never describe the area as healthy. Missing-source notes travel into the rendered brief (Step 6).

An empty result is only "nothing found" when the tool's contract says so (preflight §5). For example, an empty `activity_gaps` list without a verified-zero flag is indeterminate — it suppresses the dormant-account signals rather than proving every account is engaged.

## Step 3: Detect Signals

Read [references/signal-catalog.md](references/signal-catalog.md) from this skill's directory. It is the authoritative registry — every detectable signal, its source field, detection rule, decay profile, severity driver, and prescription template.

For each catalog entry, evaluate its detection rule against the pulled data. A rule that matches **fires** the signal and produces a candidate recommendation. Collect all fired signals before assigning horizons.

**Level vs trend signals.** Some signals detect on a single reading (a ratio below a threshold); others need a prior data point (a metric *rising*). Where the tool supplies its own change data — `arr_growth_analytics.changes`, `unified_forecast_summary` trend fields — use it. Where it does not, the signal **degrades gracefully**: fire on the level threshold alone and omit the trend qualifier from the prescription. Never skip a signal purely because trend data is absent.

**Currency is not a signal.** When `arr_growth_analytics.constant_currency.status` is `partial` or `complete` and `fx_effect` is material, read trend qualifiers on ARR-derived signals from the constant-currency `delta`, and say how much of the reported movement is currency in the evidence line. FX effect never fires a signal on its own and is never described as churn, contraction or a sales miss. `single_currency` → ignore FX entirely.

**Do not invent signals.** If the data shows something concerning that is not in the catalog, note it as a free-text observation under the most appropriate horizon, clearly marked as outside the catalog — do not fabricate a decay profile for it. The catalog is the single source of truth for horizon assignment.

## Step 4: Assign Horizons

This is the core of the skill. Every fired signal carries two properties from the catalog:

- **Urgency decay (U)** — the latest responsible moment. How long until acting no longer changes the outcome.
- **Action runway (R)** — the minimum time for the corrective action to be set up and start working.

Both map onto the horizon scale: **today** (≤1 day), **week** (≤7 days), **month** (≤30 days), **quarter** (≤90 days).

> **Horizon = the slowest bucket B such that B ≤ U and B ≥ R.**

- `B ≤ U` keeps the action in time.
- `B ≥ R` stops the brief pretending a problem is more immediately actionable than it is. This is why a severe but slow-moving signal (gross-retention erosion) is never a "today" item — there is nothing you can do today that moves it, so it belongs in the horizon where the fix can actually run.
- "Slowest in range" is deliberate: it batches work and prevents the everything-is-urgent failure mode.

**Dynamic urgency.** For some signals U is not fixed — it shrinks with context. The catalog marks these. Recompute U at detection time:

- `deal_dark_closing` — U shrinks as the close date approaches.
- `coverage_below_target`, `revenue_at_risk_spike` — U shrinks as the quarter runs out; a coverage gap with three months left is a month-horizon signal, the same gap with two weeks left is a week-horizon signal.

**The triage case (R > U).** If, at detection time, the action runway exceeds the urgency window, the signal cannot be resolved in time. Do not bury it in a horizon. Place it in a distinct **"Already Behind"** lane and frame it honestly: full recovery is not on the table; here is damage limitation. An evidence-based brief gives an honest prognosis rather than a false one.

## Step 5: Rank and Cap

### Collapse related signals first

Before ranking, merge signals that trace to one root cause — a brief that lists the same deal or rep three times is noise, not prioritisation.

- **Rep as the collapse key.** When a rep fires a Domain B signal (B2 low completion, B3 snoozed deal), fold that rep's Domain A deal-level signals into the rep recommendation — the stuck deals are symptoms, the rep is the cause. Cite the deals as evidence inside the rep's item rather than listing them as separate recommendations. (Example: a rep's stuck deal + low completion + snoozed flagged deal are one problem — coach the rep — not three.)
- **Deal as the collapse key.** Multiple signals on the same opportunity (e.g. A3 dark + A7 close date pushed) merge into one deal recommendation with combined evidence.
- **Never collapse downward across horizons.** A collapse must not move an item into a slower horizon than its own. A deal closing today (A1) stays in Today even when the same rep also has a coaching item in This Week — surface the deal in Today and reference it from the rep's item. Urgency is never sacrificed to tidy grouping.

### Rank within each horizon

Order recommendations by **severity** — the per-signal driver named in the catalog (deal amount, exposure, distance from benchmark, etc.). Severity governs *ordering within a horizon only*; it never moves a signal to a different horizon.

**Ranking a mixed horizon.** When a horizon contains different signal types whose severity drivers are not directly comparable — dollars vs percentage-point gaps vs bare percentages — rank them by **dollar exposure** as the common denominator: the deal value, rep pipeline value, or ARR the signal puts at stake. Where a driver is a bare percentage (e.g. ACV drift's `drift_pct`), use the dollar value of the pipeline it concerns as its exposure. Domain E (target-account) items carry no dollar exposure: rank them below items that do.

One override: `nrr_below_threshold` always ranks first in its horizon when it fires — net retention below 100% is the single most consequential structural signal a sales leader can have.

Caps, to keep the brief scannable:

| Horizon | Cap |
|---------|-----|
| Today | 2–5 |
| This week | 3–6 |
| This month | 3–5 |
| This quarter | 3–5 |

If more signals fire than the cap allows, keep the highest-severity ones and add a single closing line to that horizon: "+ N more lower-priority items — ask to see the full list." Never silently drop. The "Already Behind" lane is uncapped but should rarely exceed 3 items.

## Step 6: Render the Brief

Output in chat. Structure:

- A one-line header with the date.
- A one-sentence **posture** line — the single most important read on where the business stands right now.
- Each horizon as a section, in order: Today → This Week → This Month → This Quarter, then "Already Behind" only if populated.
- Each recommendation: the **prescription** (an imperative action), then on a sub-line the **evidence** (the data that triggered it) and **why this horizon** (one clause naming the decay rationale).
- Make the **owner** explicit in the prescription — "you", "coach {rep}", "{rep} to…", or "the team".
- **Amounts carry the reporting currency** from `metadata.currency` — the ISO code or an unambiguous symbol (`NZD 689K`, `€1.2M`), never a bare `$` unless the reporting currency is USD. Never add amounts from responses that report different currencies, and never convert one yourself. When a response reports `normalization: converted_excluding_unconverted` or `fx_unconverted_amounts_excluded`, say so in the evidence line of any item whose total it affects ("excludes €240k in EUR deals with no rate").
- **Forecast number cites its basis.** Wherever the brief quotes the forecast landing, use `projected_landing.value` with its basis in plain words — "reps' commit roll-up" or "weighted pipeline (fallback: {fallback_reason})"; note when it was floored at closed-won.

Omit any horizon section the leader did not ask for (per Step 1 scope), but if scope is `today` and the "Already Behind" lane is populated, still show it — a leader asking about today needs to know what has already slipped.

If any source was missing, end the brief with a **Not assessed** line listing each missing source and the areas it covers (e.g. "Not assessed: retention signals — ARR growth analytics unavailable"). Keep the wording plain; never show raw errors. If the demo label applies, place it directly under the header.

Deliver the brief in chat. Optionally, if the leader wants a copy, also save it as a Markdown file where the host saves files ([host-adapters.md](references/host-adapters.md#saving-and-delivering-files)) and give one clickable link to it.

### Output template

```
Revenue Action Brief — {date}
{one-sentence posture}

▸ TODAY — don't let the day end without these
  1. {prescription}
     Evidence: {evidence line} · Why today: {decay rationale}
  2. ...

▸ THIS WEEK
  1. {prescription}
     Evidence: {evidence line} · Why this week: {decay rationale}
  ...

▸ THIS MONTH
  1. {prescription}
     Evidence: {evidence line} · Why this month: {decay rationale}
  ...

▸ THIS QUARTER
  1. {prescription}
     Evidence: {evidence line} · Why this quarter: {decay rationale}
  ...

▸ ALREADY BEHIND — recovery window has closed; limit the damage
  - {prescription} · {evidence} · {what is and isn't still recoverable}

Not assessed: {area} — {source} unavailable   (only when a source was missing)
```

### Worked example (one item per horizon)

```
Revenue Action Brief — 21 May 2026
Quarter is on quota, but pipeline quality and gross retention are both drifting under the surface.

▸ TODAY — don't let the day end without these
  1. Re-engage Kiwi Infrastructure Partners • Executive Forecast Workspace — David to call
     directly today, not email.
     Evidence: NZD 689K Commit, 16 days since last activity, close date already passed ·
     Why today: a Commit deal silent past its close date distorts the forecast every day it sits.

▸ THIS WEEK
  1. Review pipeline qualification with the team — average deal size is drifting up 21%
     versus your trailing-12-month closed-won average.
     Evidence: ACV drift significant, current avg well above historical · Why this week:
     it's a pattern, not a cliff, but the qualification fix needs a pipeline-review cycle.

▸ THIS MONTH
  1. Diagnose the mid-market segment — win rate there is 42% versus 67%+ in every other band.
     Evidence: win rate by deal size, NZD 95K–NZD 350K band materially below the rest · Why this
     month: a blended number is hiding it; correcting it is a process change, not one action.

▸ THIS QUARTER
  1. Make gross retention a quarter priority — GRR is 49.5%, well below a healthy 90%.
     Evidence: churned ARR nearly equal to renewal ARR over the trailing year · Why this
     quarter: retention is structural — it needs sustained onboarding and CS investment.
```

## Step 7: Acting on a Brief Item (Handoff)

The brief diagnoses and prioritises — it does not draft or send. When the leader wants to act on a specific item, hand off to the execution skill that owns that kind of work, **carrying the diagnosis with it** so the output targets the real problem instead of re-deriving it from scratch.

After rendering the brief, offer once, briefly: "Want me to action any of these? Give me the item number." Do not push — if the leader doesn't take it up, stop there.

When the leader picks an item, route by the signal's domain:

| Brief item | Hand off to | Produces |
|------------|-------------|----------|
| Domain A — deal-level (A1–A6) | `deal-action-engine` | A drafted re-engagement touch targeting the diagnosed blocker |
| B2 / B3 — rep coaching | `rep-coaching-report` (prep mode) | Coaching prep / 1:1 agenda for that rep |
| B1 — your own task backlog | none | Offer to list the open items in full — it's your own to-do list, nothing to draft |
| E1–E3 — target-account pipeline generation | none | Offer to list the named accounts with their `stuck.action`, untouched accounts or `up_next` thread. The work happens in the customer's outreach workflow; this brief never creates, updates or converts target accounts or acts on stakeholder suggestions |
| B4 / B5, C*, D* — process & structural | none | Offer to break the item into concrete sub-steps, or create tracking tasks — see below |

**Handoff protocol** (for the routable rows):

1. Identify the item's `signal_id` and the entity it concerns — the opportunity ID (Domain A) or rep ID (Domain B).
2. Invoke the target skill by its plain name ([host-adapters.md](references/host-adapters.md#referring-to-other-summit53-skills)) and follow it, scoped to that entity.
3. Pass the brief's diagnosis as known context — the signal, the evidence line, and the specific blocker. This is the point of the bridge: `deal-action-engine` should draft against the obstacle the brief already identified (e.g. "silent 16 days, closes today"), not open a generic check-in.
4. These execution skills can **write** — they draft messages, create notes, and log to the CRM. The brief itself is strictly read-only. Hand off to a skill that drafts messages or writes CRM records **only after the leader has explicitly requested or approved that specific next action** in this conversation — naming the item number is a request to act on it; a general "thanks" is not. State what the target skill will do (e.g. "deal-action-engine will draft a re-engagement email for {deal}; it can also log to the CRM — go ahead?") and wait for a clear yes. The handoff is a deliberate step from diagnosis into action; name it as such. Any approval flow inside the target skill still applies.

**Domain C and D items** (pipeline-shape and structural signals) usually have no single drafted artifact — they are decisions and process changes, not one email. Do not force a handoff. Offer instead to break the item into concrete sub-steps in chat. If the leader wants tracking tasks created, that is a write: the brief does not create them; hand off to the product surface or a write-capable skill that owns tasks, under the same explicit-approval rule. Be honest that the work here is the leader's judgment, not something to generate.

One exception in Domain C: `pipeline_stall_load` (C8) *does* decompose. If the leader wants to act on it, call `deal_drag_dashboard` (read-only) for the worst-waste deals and offer to route each to `deal-action-engine` exactly as a Domain A item, under the same explicit-approval rule — so "run a stalled-deal review" becomes a set of drafted re-engagement touches, each carrying that deal's drag cause and recommended recovery action as context.

The routing targets above are the skills in the standard Summit53 library; if a deployment names them differently, the mapping is the only thing that needs adjusting — the protocol is unchanged.

## Edge Cases

- **No significant signals fire** — only when every source returned a payload may you say so plainly: "No pressing actions detected — pipeline, retention, and team execution are all within healthy ranges." If any source was missing, say instead: "No pressing actions detected in the areas assessed" and keep the **Not assessed** line — silence from a missing source is not health. Do not manufacture filler recommendations.
- **A horizon is empty** — omit the section rather than printing an empty heading.
- **Sparse CRM data** — if multiple source tools return little data, produce the brief from what fired and add one line noting the brief is partial and which areas could not be assessed.
- **Leader asks to act on an item** — this skill diagnoses and prioritises; it does not draft or send. Follow the Step 7 handoff to route the item to the execution skill that owns it. Do not draft emails or coaching materials inline.
- **Same underlying problem fires multiple signals** — apply the collapse rules in Step 5 (rep as key, deal as key, never collapse downward across horizons). Never repeat the same deal or rep across sections.

## Tools Used

`current_context` (preflight), `list_available_tools` (when the tool set is uncertain), `unified_forecast_summary`, `get_job`, `arr_growth_analytics`, `risk_heatmap`, `deal_drag_summary`, `forecast_confidence`, `team_action_plan`, `weekly_action_plan`, `activity_gaps`, `deal_drag_dashboard` (C8 handoff only), and `target_account_funnel_summary` (optional, Domain E).

All are read-only. This skill does not write to the CRM, and it hands off to write-capable skills only on the leader's explicit request or approval.

## Verification checklist

- [ ] Preflight checklist complete; `scoped_org_id` matched on returned data
- [ ] All eight data reads plus `get_job` (and the optional `target_account_funnel_summary`) preflighted; live schemas inspected
- [ ] `unified_forecast_summary` resolved through the async flow, or recorded as missing
- [ ] Every missing source has a note; only its dependent signals suppressed; nothing rendered as zero or healthy
- [ ] Collapse rules applied; caps honored with "+ N more" lines
- [ ] Domain E evaluated when `target_account_funnel_summary` is exposed, or listed as not assessed; no target-account or stakeholder writes
- [ ] Reporting currency read from the response; no bare `$` unless the reporting currency is USD; no self-computed conversions or cross-currency sums
- [ ] Excluded or unconverted amounts disclosed beside the affected totals
- [ ] Constant-currency `status` checked; FX effect never fired or worded as a performance signal; omitted for single-currency orgs
- [ ] Any forecast landing quoted with its `projected_landing.basis` and `fallback_reason`
- [ ] Demo label applied if fixtures could not be excluded
- [ ] No drafting, sending or CRM writes; any handoff explicitly requested or approved
- [ ] Brief delivered in chat; optional saved copy returned as one clickable link
