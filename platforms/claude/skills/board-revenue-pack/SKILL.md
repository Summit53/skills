---
name: "board-revenue-pack"
description: "Build a board-ready Summit53 revenue PPTX focused on what changed since the prior quarter, why it changed, and whether the evidence points to a market or execution problem. Use for board meetings, investor updates, fundraise metrics, or quarterly revenue narratives for a non-operational audience. Use forecast-delta-brief for weekly forecast calls and do not use this for a customer-facing QBR."
version: "2.2.0"
baselined: "2026-08-08"
status: "active"
---

# Board Revenue Pack

Serves **RL2 — the board meeting**. Quarterly, 2–4 weeks of prep, 20–40 hours of CRO and
RevOps time. The largest recurring artifact cost in the role.

## The moment this serves

Boards lose confidence in a CRO before CEOs do. The pack is judged against the last
three, because board members keep the prior decks. Two questions dominate:

> **"You told us last quarter this would be fixed. What's different now?"**

> **"Is this a market problem or an execution problem?"**

The second one is the whole meeting. One is forgivable and one is the CRO's fault, and
the board is asking which. A pack that reports levels without separating structural from
executional causes leaves the CRO to answer it live, unprepared.

Today: RevOps pulls numbers, the CRO writes narrative, 4–6 revision cycles, numbers move
mid-cycle and slides fall out of sync. Nobody diffs against last quarter's deck.

## What changed in this rebuild

Rebuild of `investor-revenue-report`, which produced a competent metrics deck organised
around investor metric categories rather than around the questions being asked.

- **Segment performance** (`segment_performance_summary`) is now the spine of the
  market-vs-execution answer. It was previously unconsumed by any skill.
- **Forecast confidence decomposition** supplies the "what changed and why" narrative
  instead of a static confidence score.
- **Organization revenue readiness** qualifies how much weight the ML-derived figures
  can carry — a board pack quoting a model trained on 10 months of data should say so.
- **The `revenue_engine_context` bundle** collapses roughly six granular calls into one,
  with important exceptions documented below.

---

## Step 0 — Read the references

From this skill's directory, before any calls:

- `references/delta-attribution.md` — the four-part delta contract. Every quarter-over-
  quarter number in this pack obeys it.
- `references/async-envelopes.md` — `unified_forecast_summary` and, under cache
  pressure, `segment_performance_summary` and `revenue_engine_context` return processing
  envelopes. An unhandled envelope produces a board slide with a blank number.

## Step 1 — Scope

Confirm, defaulting silently if the user says "just do it":

- **Period** — default current quarter.
- **Comparison quarter** — default the immediately prior quarter. This is the anchor for
  every delta and must appear on the slides.
- **Company name** — for the title slide.
- **What the board flagged last time** — if the user can supply it, it shapes the
  narrative directly. Ask once; do not push if they don't have it.

### The prior-deck limitation — state it up front

The board's dreaded question compares against **the prior pack**, and Summit53 stores no
generated artifacts. This skill compares against prior-period *data*, which is not the
same thing: it cannot tell you what you claimed last quarter, only what was true.

Tell the user this in chat when the pack is delivered, and if they have last quarter's
deck, offer to diff the claims manually. Do not let the pack imply a
deck-to-deck comparison it did not perform.

## Step 2 — Pull

### The bundle — one call for breadth

```
revenue_engine_context(
  sections = ["snapshot", "engine_state", "readiness",
              "segment_performance", "forecast_decomposition"],
  persona = "cro",
  fast_forecast = true,
  period_offset = 0
)
```

This replaces five separate calls. Note `metadata.granular_tools_remain_authoritative:
true` — the bundle is a convenience layer, not the source of record.

**Bundle warnings are namespaced**: `"segment_performance:no_explicit_segment_field"`,
`"forecast_decomposition:partially_instrumented"`. Split on `:` and route each warning to
the section it belongs to. Do not discard the prefix and do not drop the warning.

### ⚠ Always pass `lookback_days` explicitly — the default is day-over-day

The single most dangerous trap in this skill. Verified live on Staging:

| Call | `lookback_days` | `previous_date` | `delta_pts` |
|---|---|---|---|
| `forecast_confidence_decomposition()` — no args | `null` | 2026-08-06 | **−1.31** |
| `forecast_confidence_decomposition(lookback_days=7)` | 7 | 2026-07-31 | **−9.86** |
| `revenue_engine_context(sections=[…])` — no `lookback_days` | `null` | 2026-08-06 | **−1.31** |
| `revenue_engine_context(…, lookback_days=7)` | 7 | 2026-07-31 | **−9.86** |

**When `lookback_days` is omitted, the tool anchors to the previous daily snapshot** — a
day-over-day delta — while `period.type` still reports `"month"`. The window is not
wrong so much as unlabelled: a caller who omits the parameter gets a one-day movement
that reads like a period movement.

The bundle is **not** the problem: it propagates `lookback_days` correctly and returns
figures identical to the granular call. Pass the parameter on whichever call path you
use, and set it to the actual span of the comparison quarter (~90).

Then **echo the returned `period.previous_date` in the pack**, never the requested
window. That is the only way a reader can tell what was actually compared.

The general rule still holds — **bundle for breadth, granular where one specific
authoritative number matters** — but the reason is `metadata.granular_tools_remain_
authoritative: true`, not a discrepancy in this tool.

### Granular calls alongside the bundle

Fire in the same batch:

1. `forecast_confidence_decomposition` with `lookback_days` ≈ 90 — **the delta spine**.
2. `unified_forecast_summary` with `period_offset: 0`, `detail_level: "detailed"` —
   authoritative levels. Async: use the helper.
3. `unified_forecast_summary` with `period_offset: -1` — the prior quarter's levels, for
   deltas the decomposition does not cover. Async: use the helper.
4. `arr_growth_analytics` (`include_trends`, `include_changes`, `include_benchmarks` all
   true) — ARR, NRR, GRR, logo churn, time-to-value.
5. `arr_growth_narrative` — quote it where it surfaces a retention insight; do not
   paraphrase it into a stronger claim than it makes.
6. `renewal_forecast_summary` — portfolio-wide renewal bands. Permission-gated; on
   failure fall back to `list_account_contracts` on top accounts **and label the fallback
   in the appendix** as a top-account inference rather than a portfolio view.
7. `data_quality_score` — a footnote qualifying every other number, never a headline.

Do **not** also call `segment_performance_summary`, `organization_revenue_readiness`,
`revenue_engine_snapshot` or `revenue_engine_state` — the bundle carries them.

---

## Step 3 — Three numbers named "confidence"

Live on Staging, simultaneously:

| Source | Field | Value |
|---|---|---|
| `unified_forecast_summary` | `primary.unified_score` | **0.6425** |
| `forecast_confidence_decomposition` | `confidence.current` | **0.508** |
| `revenue_engine_snapshot` (in bundle) | `forecast.confidence_score` | **0.0** |

They measure different things over different windows. A pack that quotes one on the
headline slide and another in the appendix will be caught, and being caught on an
internal inconsistency costs more than the number itself ever could.

**Rule for this skill:**

- Headline confidence = `unified_forecast_summary.primary.unified_score`. It is the
  executive/CRO ensemble view and matches what the leader sees in-product.
- Delta narrative = `forecast_confidence_decomposition`, always labelled with its own
  band and window, and explicitly noted as a **separate measure** from the headline.
- `revenue_engine_snapshot.forecast.confidence_score` — **do not put in the pack.** It
  read 0.0 against a healthy pipeline; it is a Figure-Eight internal and will not survive
  a question.

Never present two of these as though they were the same metric at different times.

---

## Step 4 — Market problem or execution problem

The board's second question. `segment_performance_summary` (via the bundle) is what lets
you answer it rather than assert an answer.

**Reads toward *market*:** weakness concentrated in one segment while others hold;
`sales_cycle_days` lengthening across the board; `first_contract_acv` compressing
uniformly; `pipeline_coverage_gap` present in every segment.

**Reads toward *execution*:** weakness spread evenly across segments; healthy coverage
converting poorly (`pipeline_conversion_mismatch` signals); win-rate spread across
segments much wider than cycle-time spread; framework/qualification signals dominating
`engine_state.stageStates.pipeline`.

Live example, and the shape of a good finding: Enterprise win rate 44.4% (n=27) vs
Commercial 68.4% (n=38), with Enterprise carrying *higher* pipeline coverage (3.12x vs
2.73x). More Enterprise pipeline, converting worse. That is not a market-demand story —
it points at execution or qualification in the Enterprise motion. The bundle's
`pipeline_conversion_mismatches` array flags exactly this case; use it as the entry point
rather than deriving it by hand.

### Segment caveats that must appear in the pack

From live `segment_source` and `caveats`:

- **No explicit segment field is configured.** Segments are resolved from segment
  *territories* — so "Enterprise" means "the Enterprise territory", not an account-size
  classification. If the board reads it as deal-size segmentation they will draw a wrong
  conclusion. State the basis on the slide, in one line.
- **NRR/GRR are nullable per segment** until a segment has enough trailing renewal
  volume. Live: both `renewal_arr` and `expansion_arr` rolled up to **0.0** — segment-
  level retention is not yet computable. Render "not yet computable at segment level",
  never 0%.
- **Deal size is a separate lens.** Do not merge segment metrics with
  `kpis.*.by_deal_size` bands. They are different cuts and combining them is arithmetic
  nonsense.
- `rollup.win_rate.confidence` came back `"directional"` on n=65. Say "directional" on
  the slide where win rate carries an argument.

---

## Step 5 — Honesty requirements

These are not optional and they are the part of the pack that earns credibility.

### Ramp figures are survivorship-biased

`ramp_cohort` covers only reps **currently inside their ramp window**. Everyone who left
during ramp is excluded. The ramp number Summit53 can produce is therefore biased
optimistic, and a sharp CFO catches exactly this.

Live: **one rep** in ramp, whose `cohort_median_attainment_pct` (3.79%) is identical to
their own attainment because they *are* the cohort.

If a ramp figure appears anywhere in the pack it carries, adjacent to the number:

> Ramp figures cover reps currently in their ramp window (n=N) and exclude anyone who
> left during ramp. Read as a best case, not an average.

If n < 3, do not present a cohort median at all. Report the individual reps or omit the
metric. A "median" of one is a number pretending to be a statistic.

Attrition tracking is not instrumented in the platform. If the board asks for
regretted-attrition-adjusted ramp, the honest answer is that it cannot be produced today.

### Correlation is not causation

`get_revenue_loop_digest` and `list_interventions` return
`correlation: {"basis": "correlational", "causal_claim_supported": false}`.
`account_health_movement` is a trend indicator only.

Permitted: "accounts trending up outnumber those trending down this quarter."
Not permitted: any phrasing where an intervention produced an outcome. If the pack shows
interventions and outcomes together, the slide carries a one-line note that the ledger
records association within a bounded window and does not establish cause.

### Say what the pack cannot answer

Where the pack cannot answer something, the section stays and states its own limit.
Standing entries:

- **No prior-deck comparison.** Compares prior-period data, not last quarter's claims.
- **Segment retention.** Not computable at segment level this period.
- **Uninstrumented confidence drivers.** Live: forecast accuracy is `instrumented:
  false` / "building signal" and is invisible to the decomposition.
- **True loss reasons.** Loss reasons are AE-authored; price and timing are structurally
  over-represented in every CRM. A loss-reason chart is a report on what reps wrote down.
- **Model maturity.** From `readiness`: 78 closed deals, 10 months of data. ML-derived
  figures rest on that base — state it once next to the first ML-derived number.

A board pack that names its own edges unprompted is more credible than one that doesn't,
and the naming costs one slide.

---

## Step 5b — Partial-period traps

### `arr_growth_analytics.changes` — now MTD-matched, still read the basis

Fixed server-side on 8 Aug 2026. `changes` now matches the comparison window:

```json
"changes": {"current_period": "2026-08", "previous_period": "2026-07",
            "observed_through": "2026-08-08", "previous_observed_through": "2026-07-08",
            "comparison_basis": "month_to_date_vs_prior_month_to_date",
            "comparison_status": "comparable_partial_periods", "comparable": true,
            "warnings": ["partial_period_mtd_comparison"]}
```

The prior figure dropped from $5,250,418 (all of July) to $1,640,390 (1–8 July), so the
delta is now like-for-like. The old "Total ARR down 100%" artifact is gone.

**Still required of the pack:** render `comparison_basis` and `observed_through` on the
slide. An MTD-vs-MTD comparison over 8 days is a legitimate but small and noisy sample,
and a board reading "down $1.6M" without knowing it covers eight days will misread it.
Check `comparable` before using `changes` at all, and surface any entry in
`changes.warnings`.

**Empty-window mix is now handled server-side.** The mix change entry is suppressed
rather than emitted as a false −100%, and the reason is declared:

```json
"changes": {"warnings": ["partial_period_mtd_comparison", "current_arr_mix_unavailable"],
            "changes": [{"key": "total_arr", …}]}          ← no new_business_pct entry
```

Genuine zero is preserved and distinguishable. Every mix-bearing block now carries an
availability triplet:

```json
"arr_mix": {"new_business_pct": 50.4, …,
            "availability": "available", "status": "calculated",
            "evidence": {"denominator_arr": 10419303.26, "opportunity_count": 50}}
```

Present on `arr_mix`, `indexes`, `benchmark_comparison.arr_mix_comparison` and
`gap_to_target`.

**Check `availability` before rendering any mix figure**, and read
`evidence.opportunity_count` before letting a percentage carry an argument — a mix
computed over a handful of deals is arithmetically valid and rhetorically worthless. If
`current_arr_mix_unavailable` appears in `changes.warnings`, say the mix is not computable
for the window rather than leaving the reader to notice a missing row.

Apply the same check to any `trends.points` series — the live series has `total_arr: 0.0`
for six of twelve months, including the current one. Charting it raw draws a line
collapsing to zero. Filter to periods with `data_quality.confidence_level` other than
`insufficient` before charting, and state how many periods were excluded.

### ARR has three different values too

Live, simultaneously: `total_arr` **$10,419,303** (rolling 12-month, by type),
`arr_band.current_arr` **$17,242,873** (closed-won base), and
`segment_performance.rollup.active_contract_arr` **$27,267,436** (active contract ARR
across segments).

Pick one, define it on the slide, and use it consistently. For a board pack, **active
contract ARR** is usually the right headline (it is what the company actually has under
contract); `total_arr` is a period-scoped flow measure and reads as a much smaller
company. Whichever is chosen, the definition goes on the slide.

### NRR is estimated, and the pack must say so

`nrr.methodology` is `"estimated"` and `nrr.limitations` lists: does not include revenue
contractions, churn based on Closed Lost renewals only, no beginning-of-period baseline.

An NRR of 120.7% that excludes contractions is not comparable to a properly computed NRR,
and "Elite tier" is the tool's label for the value, not a verified standing. Carry the
limitations as a footnote wherever NRR appears. Note also that `nrr.confidence` varies by
period in the trend series (`high` / `medium` / `low` / `insufficient`) — do not chart
points where it is `insufficient`.

---

## Step 6 — Do not render these as percentages

`revenue_engine_snapshot.conversion_rates` contains values above 1.0 — live:
`replied_to_pipeline: 3.6667`, `expansion_to_renewed: 2.7`, `working_to_engaged: 1.3469`.

These are **ratios between independently-counted stage populations**, not funnel
conversion percentages. Rendering them with a `%` suffix puts "366% conversion" on a
board slide. Either present them as ratios with an explicit denominator, or leave them
out. `conversion_rates_by_deal_size.pipeline_to_won` is a genuine rate (all values ≤1)
and is safe.

---

## Step 7 — Build the deck

Read the `pptx` skill's `pptxgenjs.md` reference for mechanics.

**Design system** — Midnight Executive, unchanged from the prior version for continuity
with decks the board has already seen: Navy `1E2761`, Ice Blue `CADCFC`, Emerald
`10B981`, Amber `F59E0B`, Red `EF4444`, Charcoal `1E293B`, Off-white `F8FAFC`, Slate
`64748B`. Georgia headers 36–44pt, Calibri body 14–16pt, 16:9, 0.5" margins.

> ⚠ **Set `pptx.layout = "LAYOUT_WIDE"`, not `"LAYOUT_16x9"`.** Both are 16:9, but
> `LAYOUT_16x9` is **10" × 5.625"** while `LAYOUT_WIDE` is **13.33" × 7.5"**. Coordinates
> written for a 13.33" canvas silently render off-slide on `LAYOUT_16x9` — the deck
> generates without error and the right-hand third of every slide is missing. This was
> hit during test build and only caught by rendering slides to images. Verify with:
> `pdftoppm` the PDF and confirm the rightmost element is visible.

### Slides — 8, ordered by the questions

1. **Title** — navy. Company, "Revenue Review", quarter, comparison quarter.
2. **What changed since last quarter** — the delta-with-attribution slide, built per
   `references/delta-attribution.md`: level, movement, contributor table, residual,
   uninstrumented rows marked. This slide answers the board's first question and belongs
   **before** the ARR slide. The prior version buried it; the board asks it first.
3. **ARR and retention** — ARR with growth delta; NRR and GRR paired (a wide gap means
   expansion is masking churn — call it out in one line); logo churn; time-to-value.
   `data_quality_score` as a corner footnote.
4. **Market or execution** — segment table (ARR, win rate + n, coverage, cycle days,
   ACV), the `pipeline_conversion_mismatches` signals, and one explicit sentence naming
   which way the evidence points and how strongly. Segment-basis caveat line beneath.
5. **Pipeline and forecast** — coverage, quota attainment, commit/best-case/pipeline,
   win rate by deal-size band, ACV drift (only flagged when `is_significant: true`).
6. **Renewals and customer health** — renewal bands from `renewal_forecast_summary`,
   logo churn, account health movement worded as a trend.
7. **What we cannot yet answer** — the limits from Step 5, as a slide. Do not bury this
   in an appendix. It is the credibility slide.
8. **Close** — navy, mirrors the title.

Prefer native PptxGenJS charts (BAR, DOUGHNUT) over images — editable in PowerPoint,
which matters because this deck goes through 4–6 revision cycles.

### Aggregation rule

No rep names, no deal names, no account names in the pack. Segment-, band- and
portfolio-level only. This survived from the prior version and is correct: a board pack
that names a rep invites a conversation the CRO does not want to have in that room.

## Step 8 — Verify

1. Generate, convert to images (`soffice.py` → `pdftoppm`), and **look at every slide**.
2. Content checks, not exit status:
   - Is the Step 2 delta slide populated with real contributor values, or is it blank
     because an async envelope was read as data?
   - Does exactly one confidence number appear as the headline, with the decomposition
     labelled as a distinct measure?
   - Do any percentages exceed 100 where a rate is implied?
   - Are segment retention cells "not yet computable" rather than 0%?
   - Does any ramp figure appear without the survivorship caveat adjacent to it?
   - Is the limits slide present and non-empty?
   - Search the deck text for "caused", "because", "drove", "resulted in". Rewrite each.
3. Fix and re-verify. Do not declare done until one full fix-and-verify cycle has run.

A deck that generates without erroring but has a blank contributor table has failed.

## Tools

| Tool | Role |
|---|---|
| `revenue_engine_context` | Bundle: snapshot, engine_state, readiness, segment_performance, forecast_decomposition (cross-check only) |
| `forecast_confidence_decomposition` | **Authoritative** delta and attribution — call granularly with an explicit `lookback_days` |
| `unified_forecast_summary` | Headline confidence and levels, current and prior period (async) |
| `get_job` | Async lifecycle |
| `arr_growth_analytics` | ARR, NRR, GRR, logo churn, time-to-value |
| `arr_growth_narrative` | Retention narrative, quoted not paraphrased |
| `renewal_forecast_summary` | Portfolio renewal bands (permission-gated) |
| `list_account_contracts` | Labelled fallback for the above |
| `account_health_movement` | Health trend, correlational wording only |
| `data_quality_score` | Footnote qualifier only |
