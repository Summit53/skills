---
name: "forecast-delta-brief"
description: "Produce a one-page forecast delta brief for a weekly forecast or commit call, explaining the current number, how it moved since the prior call, and which contributors account for the movement. Use for forecast-call preparation, commit reviews, pipeline reviews, forecast changes, confidence movement, weekly forecast briefs, or questions such as 'why is it different from last week?'. Use board-revenue-pack for quarterly board narratives."
version: "2.4.0"
baselined: "2026-08-08"
status: "active"
---

# Forecast Delta Brief

Serves **RL1 — the weekly forecast / commit call**. One page, produced in under a minute,
that a revenue leader reads on the way into the room.

## The moment this serves

Weekly, 60–90 minutes, with managers and RevOps. At quarter-end the CEO and CFO join,
which changes the room. This is where the CRO's own number to the CEO gets assembled, and
credibility here is cumulative — a pattern of unexplained revision ends CRO tenures.

The dreaded question is **not** "what's the number?". The CRO can always produce a
number. It is:

> **"Why is it different from what you told me last week?"**

Today that gets answered by RevOps diffing two snapshots in Excel (2–4 hours weekly), or
by the CRO stitching together verbal manager answers on the way into the room. The honest
answer is usually "a few deals slipped" without knowing which, or why.

**This skill produces the defensible account of the delta.** It is not a dashboard and
not a health report. If it tells you the level without telling you what moved it, it has
failed at its only job.

## What replaced what

This is a rebuild of `revenue-monitor`, which compared against **4 weeks prior**. The
hot seat is weekly: the number being defended is the one reported **seven days ago**. A
4-week window cannot answer the question being asked.

`forecast_confidence_decomposition` — purpose-built for this and previously unconsumed by
any skill — is now the core tool. The snapshot-diffing machinery it replaces is retained
only as a fallback for metrics the tool does not decompose.

---

## Step 0 — Read the references

Read both from this skill's directory before making any calls:

- `references/delta-attribution.md` — the four-part delta contract, additivity checking,
  instrumentation honesty, causal-language rules. **This is the skill's spine.**
- `references/async-envelopes.md` — `unified_forecast_summary` returns a processing
  envelope on a cold cache. Reading it as data produces a brief with a blank headline
  and no error.

## Step 1 — Establish the window

Default comparison is **7 days** — the last forecast call. Override only if the user
names a different one ("since the last board meeting", "vs the start of the quarter").

If the user names a cadence other than weekly, set `lookback_days` to match and **label
the artifact with the actual returned `previous_date`**, not the requested window. Per
the reference: `period.type` describes the reporting bucket, not the comparison window —
a `lookback_days: 7` call legitimately returns `period.type: "month"`. Report the window
as `previous_date → current_date` and never from `period.type`.

## Step 2 — Pull

Fire all of these in one batch. The forecast poll then overlaps the others.

**Core — the delta and its attribution:**

1. `forecast_confidence_decomposition` with `lookback_days: 7`
   Parts 2–4 of the delta contract come from here. Everything else is corroboration.
2. `unified_forecast_summary` — the authoritative levels: `quota_metrics`,
   `kpis.pipeline_coverage`, `revenue_at_risk`, `forecasts.manual.commit`.
   **Route through the async helper.**

   ⚠ **It cannot give you last week's levels.** It is period-scoped — it reports the
   quarter, and `period_offset: -1` returns the *prior quarter*, not the prior week.
   Only `forecast_confidence_decomposition` carries a week-over-week comparison. So the
   levels table renders current values with **blank deltas**, and the brief says why.
   Do not fill those cells with a quarter-over-quarter figure — a mislabelled delta in
   this artifact is the exact failure it exists to prevent.

**Corroboration — which deals are behind the move:**

3. `risk_heatmap` (`page_size: 50`, **`sort_direction: "asc"`** — see the trap below).
   Paginate: read `total` on the first response and page until every row is retrieved.
4. `get_opportunity_signals` for the top 3 troubled deals by value — the first-constraint
   on each, used to name what is actually blocking them.
5. `coaching_intervention_plan` — whether the reps behind the moved deals are already
   flagged. **Gated on `coaching_flag_quality`** (see below).

Do not pull more than this. The brief is one page and the leader has 60 seconds. Every
additional call is latency against a deadline.

### `risk_heatmap` score semantics — read them, don't assume them

Fixed server-side on 8 Aug 2026. The response now declares its own semantics:

```json
"score_semantics": {"primary_field": "healthScore",
                    "direction": "higher_is_healthier",
                    "riskiest_first": {"sort_by": "healthScore", "sort_direction": "asc"},
                    "deprecated_aliases": {"riskScore": "healthScore"},
                    "source": "stored_snapshot", "freshness_seconds": 300}
```

**Drive the call from `score_semantics.riskiest_first`.** Default ordering is now
riskiest-first, and `risk_level: "high"` correctly returns low-health deals (24 of 72).
Each row also carries `healthBand` (`Low` / `Medium` / `High`) — prefer it over
hand-rolled thresholds.

### ⚠ `healthScore` deltas — still suppressed, for a narrower reason

S53-005 (calculator-path divergence) was **fixed and deployed** on 8 Aug 2026, commit
`480443bc`. Both write paths now use one canonical engine, so **ongoing** path drift is
gone.

**One residual reason to keep suppressing deal-level score deltas.** At the time of
writing, 163 stored scores carry canonical provenance and **79 legacy rows remain**.
Each of those will step-change once, when the reconciler next writes it — a migration
artifact, not a business movement. And because `calculator_version` is
**database-only and not exposed over MCP**, this skill has no way to tell a canonical row
from a legacy one.

So, until the legacy backlog drains and provenance is exposed:

- **Do not render a `healthScore` delta.** The brief's headline delta comes from
  `forecast_confidence_decomposition`, which is unaffected — keep it that way.
- Quote `healthScore` only as a **current-state band** (`healthBand`) when naming deals
  that corroborate the confidence driver, never as "improved" or "deteriorated".
- A deal within ~0.06 of a band boundary may cross it on a legacy→canonical rewrite
  without anything changing. Call such a band marginal.

**Lift this restriction when** `score_semantics.calculator_version` (or a per-row
`calculatorVersion`) appears *and* reports zero legacy rows. Do **not** lift it on the
basis of scores looking stable — during a period when only one writer is active, agreeing
values prove nothing about provenance.

**Do not use `riskScore`.** It survives as a deprecated alias of `healthScore` and
returns identical values, so `sort_by: "riskScore", sort_direction: "desc"` returns the
**healthiest** deals. Using it now raises a machine-readable warning:

```json
"warnings": ["deprecated_risk_sort_alias"],
"metadata": {"warning_details": [{"code": "deprecated_risk_sort_alias",
  "parameter": "sort_by", "value": "riskScore", "replacement": "healthScore",
  "semantics": "higher_is_healthier",
  "riskiest_first": {"sort_by": "healthScore", "sort_direction": "asc"}}]}
```

**Treat `deprecated_risk_sort_alias` as a hard error in this skill.** If it appears, the
call used the wrong field — re-issue with `healthScore` rather than interpreting the
result. Verified no false positive: a `healthScore asc` call returns `warnings: []`.

### Factor names are now truthful — use the canonical set

`riskFactors` now carries canonical higher-is-healthier names alongside legacy aliases,
with semantics declared in `score_semantics.factor_semantics`:

| Canonical | Legacy alias | Meaning |
|---|---|---|
| `frameworkCompleteness` | — | framework evidence completeness |
| `contactEngagement` | `contactRisk` | stakeholder engagement |
| `activityMomentum` | `activityDrag` | opportunity activity momentum |
| `repCommitConfidence` | `repCommitLevel` | forecast-category commitment confidence |

All four are `higher_is_healthier` on a 0.0–1.0 scale. **Use the canonical names.** The
legacy keys are emitted with identical values, so `activityDrag: 1.0` on the healthiest
deal still reads as "maximum drag" to anything still using the old name — and unlike the
sort alias, reading a legacy field raises no warning. Cite sub-scores only by canonical
name, and quote the `meaning` string when a sub-score carries an argument.

### Check `scoreStatus` before quoting a deal

Every row now carries `scoreStatus` (`fresh` / `stale`), `scoreCalculatedAt`,
`scoreAgeSeconds` and `scoreRefreshPending`, against a `freshness_seconds: 300` budget.

On an unscheduled environment these are routinely stale — observed at 27,947 s (7.8 h),
roughly 93× the freshness window, with `scoreRefreshPending: false` meaning **nothing is
queued to fix it**. Until the production refresh job is scheduled, expect stale scores.

If any quoted deal is `stale`, say so in the brief with its age. Do not call the tool
with `refresh: true` to force freshness — that recomputes and persists scores, which is
a write, and this skill is read-only by design.
### The `coaching_intervention_plan` flag gate

The server now classifies its own flag quality. **Read it; do not compute a base rate.**

```json
"coaching_flag_quality": {"classification": "non_discriminating",
  "evaluated_reps": 19, "flagged_reps": 18, "flag_rate": 0.9474,
  "non_discriminating_threshold": 0.75,
  "warning": "The coaching flag applies to at least 75% of evaluated reps and must not
              be used as an ordinal performance ranking."},
"ordering": {"ordinal_ranking": false, "basis": "cohort_then_name"}
```

If `classification` is `non_discriminating`, **drop the section** — say the coaching flag
is not discriminating this week and move on. Naming a rep on the basis of a near-universal
flag is the kind of thing that gets repeated in a room and cannot be defended when checked.

Never render a priority rank. `ordering.ordinal_ranking: false` prohibits it, and the
underlying ties are real (three reps at 0.8558, three at 0.6100).

Per-rep, prefer `evidence_sufficiency.persistent_needs_coaching` over the raw flag. Live
it is `false` for every rep — one observed week against a two-week minimum.

## Step 3 — Build the delta

Follow `references/delta-attribution.md` exactly. In summary:

1. Take `confidence.delta_pts` as the headline. Do not recompute it.
2. Sum `contribution_pts` across contributors; compare to the headline; render the
   residual honestly if it is ≥0.1 pts.
3. Render uninstrumented contributors as *not yet measured* — never as 0.0.
4. Flag contributors sitting in a `critical` or `watch` band while contributing ~0 to the
   delta as **standing conditions**. They did not move; they are also not fine.
5. If `warnings` contains `partially_instrumented`, carry the qualifier line.

### Attaching deals to the movement

The decomposition names a driver. The room wants deal names. Bridge them, carefully:

- Take the top movers from `risk_heatmap` and check whether their risk type matches the
  worsening driver (e.g. `execution` worsening ↔ deals with activity or stage-velocity
  risk; `data_quality` ↔ deals with missing fields).
- Name **at most three deals**, with value, stage, and the first-constraint from
  `get_opportunity_signals`.
- Word the link as consistency, not causation: *"consistent with the execution decline"*,
  not *"which caused the decline"*. `risk_heatmap` is a current-state read; it does not
  carry a week-ago comparison, so it can corroborate the direction but cannot prove
  which deals moved the score.
- If no deal-level pattern matches the driver, **say so**: "No individual deal explains
  the movement; the decline is distributed across the portfolio." That is a real and
  useful finding — it redirects the conversation from deal rescue to systemic execution.

## Step 4 — Render

Markdown, one page, saved to the outputs folder as
`Forecast-Delta-Brief-{YYYY-MM-DD}.md`. Print it in chat as well — this artifact is
usually read on a phone walking into a meeting, so chat delivery is the primary path and
the file is the record.

```markdown
# Forecast Delta Brief — {current_date}
Comparison window: **{previous_date} → {current_date}** ({n} days)

## The line
{One sentence: level, movement, dominant driver, window. This is what the leader says
in the room. It must be defensible verbatim.}

## What moved it
{Attribution table per delta-attribution.md — Was / Now / Moved / Contribution / Band,
ordered by |contribution_pts| desc, uninstrumented rows last, total and residual row.}

{Qualifier line if partially_instrumented.}

## Standing conditions — did not move, still bad
{Contributors in critical/watch bands with ~0 contribution. Omit the section entirely
if there are none — do not render an empty heading.}

## The deals behind it
{≤3 deals: name, value, stage, first-constraint. Or the explicit
"no individual deal explains the movement" statement.}

## Levels (for reference, not the story)
| | Now | Prior | Δ |
|---|---|---|---|
| Commit | | | |
| Pipeline coverage | | | |
| Quota attainment | | | |
| Revenue at risk | | | |

## What this brief cannot tell you
{Explicit limits — see below. Never omit this section.}

---
Sources: {tools called, with any async notes verbatim}
```

### The limits section is mandatory

Where the brief cannot answer something, it says so **in the brief** rather than omitting
the section. Standing entries, included whenever they apply:

- **Uninstrumented drivers.** "Forecast accuracy is not yet instrumented ('building
  signal'), so any movement in it is invisible to this decomposition."
- **Deal attribution is corroborative.** "`risk_heatmap` reports current state, not a
  week-ago comparison. Deals listed are consistent with the driver that moved; they are
  not proven to have moved it."
- **Residual.** Where residual ≥0.1 pts: "X of the Y-point move is not attributed to any
  instrumented driver."
- **Coaching flag base rate.** Where suppressed: "The coaching flag fired on N of M reps
  this week and is not discriminating; it has been excluded."
- **Missing sources.** Any `note` returned by the async helper, verbatim.

A leader who knows the edge of the artifact can defend the middle of it. One who
discovers the edge in the room cannot.

## Step 5 — Verify before delivering

Check the content, not the exit status. A brief that generates cleanly and says nothing
has failed.

1. Is the headline delta present and non-null? If the decomposition returned no prior
   reading, the brief must say "no prior reading" — not render a blank.
2. Do the contributions sum to the headline within 0.1 pts, or is the residual rendered?
3. Is every uninstrumented contributor marked *not yet measured* rather than 0.0?
4. Does the lead sentence contain: level, delta, driver, and the window dates?
5. Is the limits section present and non-empty?
6. Does any sentence claim causation? Search the draft for "caused", "because",
   "drove", "will restore", "led to". Rewrite each.

Fail any of 1–5 and the brief is not ready to ship.

---

## Scheduling

Pairs with the `schedule` skill. Run the morning of the forecast call — the brief is
about the last 7 days, so it must be fresh.

```
cronExpression: "0 7 * * 1"   # Mondays 7am, adjust to the call
```

Prompt: *"Run the forecast delta brief with a 7-day comparison window and email it to
{user_email}. Include the limits section."*

Unlike the skill it replaces, this one writes nothing back to the CRM. It is a
read-and-render artifact — there is no note-writing step, no deduplication, and no
approval gate to manage.

## Tools

| Tool | Role |
|---|---|
| `forecast_confidence_decomposition` | Delta and contributor attribution — **core** |
| `unified_forecast_summary` | Authoritative levels (async — use the helper) |
| `get_job` | Async lifecycle for the above |
| `risk_heatmap` | Deal-level corroboration (paginate) |
| `get_opportunity_signals` | First-constraint per named deal |
| `coaching_intervention_plan` | Rep flag — gated on base-rate check |
