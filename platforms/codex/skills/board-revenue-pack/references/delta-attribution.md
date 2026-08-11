# Delta With Attribution — Canonical Pattern

**Canonical file. Version 1.0.1 · adapted for Summit53 Staging.**

Maintained once, copied byte-identical into every consuming skill. Bump the version on
edit and re-copy. If two copies disagree, the higher version wins.

Intended consumers (Phase 4 items 1, 2, 5): `forecast-delta-brief` (built),
`board-revenue-pack` (built), CS Renewal Forecast (Tier 2, not yet built — this pattern
is designed to accept it without modification).

## Contents

- [Why this exists](#why-this-exists)
- [Four-part contract](#the-four-part-contract)
- [Primary source](#primary-source-forecast_confidence_decomposition)
- [Additivity and instrumentation](#verify-additivity-before-rendering)
- [Standing conditions](#contributors-with-a-bad-level-but-no-movement)
- [Rendering](#rendering)
- [Metrics without decomposition](#applying-the-pattern-to-metrics-without-a-decomposition-tool)
- [Causal-language rule](#causal-language--hard-rule)

---

## Why this exists

Nobody is ever in a hot seat about a current-state number. They are in a hot seat about
the **movement**, and whether they can account for it.

- "Why is it different from what you told me last week?" (weekly forecast call)
- "You told us last quarter this would be fixed. What's different now?" (board)
- "Which accounts are at risk next quarter, and how confident are you?" (NRR review)

All three are the same shape. A leader can always produce a number. What they frequently
cannot produce is a **defensible account of the delta**. That is what this pattern
produces, and it is why it is built once rather than three times.

---

## The four-part contract

Every delta rendered by any consuming skill answers four questions in this order. The
order is not cosmetic — it is the order the question gets asked in the room.

| Part | Question | Requirement |
|---|---|---|
| **1. Level** | What is the number now? | Current value, units, as-of timestamp |
| **2. Movement** | What was it, and what changed? | Prior value, prior-as-of, signed delta, direction |
| **3. Attribution** | What moved it? | Contributor-by-contributor decomposition, signed, summing to the total |
| **4. Coverage** | How much of the move is explained? | Explained vs residual, and what is not instrumented |

A delta missing part 3 is a dashboard. A delta missing part 4 is a dashboard that
overstates its own authority. **Never render 1–3 without 4.**

---

## Primary source: `forecast_confidence_decomposition`

This tool is purpose-built for parts 2–4 and, before this rebuild, had zero consumers.
It is the tightest pain-to-tool match in the catalogue. Live shape from Staging:

```json
{"data": {
  "as_of": "2026-08-07",
  "period": {"type": "month", "current_date": "2026-08-07",
             "previous_date": "2026-07-31", "lookback_days": 7},
  "confidence": {"current": 0.508, "previous": 0.606, "delta": -0.0986,
                 "delta_pts": -9.86, "band": "watch", "direction": "negative"},
  "contributors": [
    {"key": "pipeline_shape",      "label": "Pipeline shape",   "current": 0.0,  "previous": 0.0,
     "delta": 0.0,    "weight": 0.333, "contribution_pts": 0.0,   "band": "critical", "instrumented": true},
    {"key": "execution",           "label": "Execution health", "current": 0.516,"previous": 0.871,
     "delta": -0.355, "weight": 0.278, "contribution_pts": -9.86, "band": "watch",    "instrumented": true},
    {"key": "data_quality",        "label": "Data quality",     "current": 0.89, "previous": 0.89,
     "delta": 0.0,    "weight": 0.222, "contribution_pts": 0.0,   "band": "healthy",  "instrumented": true},
    {"key": "account_renewal",     "label": "Account & renewal","current": 1.0,  "previous": 1.0,
     "delta": 0.0,    "weight": 0.167, "contribution_pts": 0.0,   "band": "healthy",  "instrumented": true},
    {"key": "historical_accuracy", "label": "Forecast accuracy","current": null, "previous": null,
     "delta": null,   "weight": 0.0,   "contribution_pts": null,  "band": null,
     "instrumented": false, "note": "building signal"}],
  "primary_driver": "execution",
  "drivers_worsening": ["execution"],
  "drivers_improving": []},
 "warnings": ["partially_instrumented"]}
```

Key fields, and what each is for:

- `confidence.delta_pts` — the headline movement, already in percentage points. Use it
  directly; do not recompute from `current`/`previous` and risk a rounding mismatch with
  the contributor figures.
- `contributions_pts` per contributor — **signed, and denominated in the same units as
  the headline.** This is what makes the decomposition additive and therefore defensible.
- `instrumented: false` — the contributor exists in the model but is not yet measurable.
  It is not zero. See "Instrumentation honesty" below.
- `primary_driver` / `drivers_worsening` / `drivers_improving` — the tool's own read.
  Use it to order the narrative; do not contradict it silently. If your own arithmetic
  disagrees, say both.

### The `lookback_days` control

`lookback_days` sets the comparison anchor. `lookback_days: 7` returned
`previous_date: 2026-07-31` against `current_date: 2026-08-07` — a **week-over-week**
comparison, which is what the weekly forecast call needs.

Note the returned `period.type` was `"month"` while `lookback_days` was 7. `period.type`
describes the reporting period bucket, not the comparison window. **Always report the
comparison window from `period.previous_date` → `period.current_date`, never from
`period.type`.** Getting this wrong mislabels a week-over-week delta as monthly, which
is precisely the credibility failure the artifact exists to prevent.

Anchors by consumer:

| Consumer | `lookback_days` | Comparison |
|---|---|---|
| Forecast Delta Brief (RL1) | `7` | Last week — the CRO reported a number 7 days ago |
| Board Revenue Pack (RL2) | `~90` | Last quarter — the board holds the prior deck |
| CS Renewal Forecast (CS2) | `~90` | Last quarterly review |

Always echo the actual returned `previous_date` in the artifact rather than the
requested window. If the tool anchors somewhere other than where you asked, the reader
must see where it actually anchored.

---

## Verify additivity before rendering

The contributions should sum to the headline delta. Check it, every run:

```python
explained = sum(c["contribution_pts"] for c in contributors
                if c.get("contribution_pts") is not None)
residual  = confidence["delta_pts"] - explained
```

In the live sample: `explained = -9.86`, `delta_pts = -9.86`, `residual = 0.0` — fully
explained by a single driver.

Handle the result honestly:

- `|residual| < 0.1 pts` — treat as fully explained. Do not render a residual line for
  floating-point dust.
- `|residual| >= 0.1 pts` — render it as an explicit **"unexplained"** row in the
  attribution table. Do not silently rescale contributors to close the gap, and do not
  drop the smallest contributor to make the arithmetic look tidy. An unexplained residual
  is a real finding about model coverage.
- `|residual| > 50% of |delta_pts|` — the decomposition is not carrying the movement.
  Lead the narrative with that fact rather than with the largest named contributor.
  Attributing a move to a driver that explains a minority of it is the sophisticated
  version of making it up.

---

## Instrumentation honesty

A contributor with `instrumented: false` is **not a zero contributor**. It is a
contributor whose movement is unmeasured. The distinction is the whole ballgame in a
board room: "renewal risk didn't move" and "we cannot yet see whether renewal risk moved"
are different sentences, and only one of them survives a follow-up question.

Rules:

1. Render uninstrumented contributors in the attribution table with an explicit
   `not yet measured` marker and their `note` text (e.g. `"building signal"`). Never
   omit the row, and never render it as `0.0`.
2. If `warnings` contains `partially_instrumented`, carry a one-line qualifier under the
   attribution block: *"N of M confidence drivers are instrumented; the remainder are
   building signal and are excluded from the decomposition."*
3. A contributor with `weight: 0.0` carries no weight in the current model. Say so
   rather than showing it as an unimportant-looking small number.

---

## Contributors with a bad level but no movement

`pipeline_shape` in the live sample: `current: 0.0`, `band: "critical"`,
`contribution_pts: 0.0`. It contributed **nothing to the delta** and is simultaneously
the **worst-performing driver in absolute terms**.

Both facts are true and the artifact must carry both. The delta narrative correctly says
execution moved the number. A reader who stops there concludes pipeline shape is fine.

Render level and movement in separate columns, and where a contributor sits in a
`critical` or `watch` band while contributing ~0 to the delta, add a standing-state note:

> Pipeline shape did not move this week and is not part of the decline. It has been at
> `critical` in both readings — a persistent condition, not a new one.

"It didn't get worse" is not "it is fine". Conflating the two is how a chronic problem
stays invisible across a run of weekly briefs.

---

## Rendering

Attribution table, ordered by `|contribution_pts|` descending, uninstrumented rows last:

| Driver | Was | Now | Moved | Contribution | Band |
|---|---|---|---|---|---|
| Execution health | 0.871 | 0.516 | −0.355 | **−9.9 pts** | watch |
| Pipeline shape | 0.000 | 0.000 | 0.000 | 0.0 pts | critical ⚠ standing |
| Data quality | 0.890 | 0.890 | 0.000 | 0.0 pts | healthy |
| Account & renewal | 1.000 | 1.000 | 0.000 | 0.0 pts | healthy |
| Forecast accuracy | — | — | — | *not yet measured* | building signal |
| | | | **Total** | **−9.9 pts** | residual 0.0 |

Lead sentence — level, movement, driver, window, in one line:

> Forecast confidence is **50.8%**, down **9.9 points** from **60.6%** on 31 Jul.
> Effectively all of the decline is execution health (−9.9 pts), which fell from 0.87 to
> 0.52. No other instrumented driver moved.

This is the sentence the leader repeats in the room. It must be defensible verbatim, so
it carries the window and the attribution, not just the number.

---

## Applying the pattern to metrics without a decomposition tool

Most metrics have no purpose-built decomposition. The four-part contract still applies —
parts 3 and 4 are built by hand from a comparable prior reading.

1. **Establish the prior honestly.** Prefer a tool that returns its own comparison
   (`forecast_confidence_decomposition`, `account_health_movement`,
   `arr_growth_analytics.changes`, `unified_forecast_summary.primary.trend`). Only fall
   back to a stored snapshot when no tool carries the comparison. Never compare against a
   number a previous run wrote into prose — reparse from a stored raw response or drop
   the comparison.
2. **Decompose along a dimension the audience already thinks in** — segment, stage,
   rep, deal-size band, renewal window. Not along whatever the API happens to return.
   `segment_performance_summary` is the natural decomposition axis for ARR and win rate;
   `kpis.*.by_deal_size` for coverage and win rate.
3. **Check additivity the same way**, and render the residual the same way.
4. **State the comparison basis in the artifact.** "vs the snapshot stored 2026-08-01"
   is defensible. "vs last week" without a date is not.

### When there is no prior reading

Say so, in the artifact, in the position the delta would have occupied:

> **No prior reading.** This is the first brief for this metric, so there is no delta to
> attribute. The level is reported below; comparison begins next run.

Do not compare against a default, an industry benchmark, or a target and present it as a
delta. A gap-to-target is a different quantity from a movement, and the hot-seat question
is about movement.

---

## Causal language — hard rule

The decomposition is **arithmetic attribution**, not causal inference. It says which
component of a weighted score moved, not why it moved or what to do about it.

Permitted:
- "Execution health accounts for 9.9 points of the 9.9-point decline."
- "Confidence fell alongside a drop in execution health."
- "The decline is concentrated in execution health."

Not permitted:
- "Execution health *caused* the forecast to drop."
- "*Because* execution slipped, confidence fell."
- "Fixing execution *will* restore 9.9 points."

This is not pedantry. A contributor is a component of a formula; movement in it is
movement in the output by construction. Claiming causation invites "so if we fix that,
the number comes back?" — and the honest answer is that nobody knows, which is a bad
answer to give after implying otherwise.

`get_revenue_loop_digest` and `list_interventions` carry
`correlation: {"basis": "correlational", "causal_claim_supported": false}` in their
responses. Where a consuming skill uses either, that flag must be honoured in the
artifact's wording. See each skill's own notes.
