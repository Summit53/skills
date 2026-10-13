---
name: "board-revenue-pack"
description: "Build a board-ready Summit53 revenue pack (8-slide PPTX, optional regional slide) for a non-operational audience: what changed since last quarter, what arithmetically accounts for it, and whether the evidence points to a market, execution or currency explanation. Pulls ARR, retention, segment performance, the quarterly forecast-confidence decomposition, pipeline, renewals, account health and data readiness, and stops safely when no genuine prior-quarter anchor exists. Use when a user says 'build my board deck', 'board revenue pack', 'prep the numbers for the board', 'investor update', 'I have a board meeting', 'quarterly revenue deck for investors', 'the board is going to ask why this changed', 'is this a market or execution problem', or 'fundraise deck with live metrics'. Do not use for the weekly forecast call — use forecast-delta-brief. Do not use for an internal quarterly operating review — use qbr-generator. Do not use for a customer-facing review — use customer-qbr."
version: "2.4.1"
baselined: "2026-10-13"
status: "active"
---

# Board Revenue Pack

Build an eight-slide (nine with the optional regional view), read-only board or investor
revenue pack that answers three questions from evidence: what changed since the prior
quarter, what arithmetically accounts for the change, and whether the pattern looks
structural (market), executional, or — for multi-currency organizations — partly currency.
The pack reports evidence and its limits. It never names reps, deals, or accounts.

## Route first

- Weekly forecast or commit call, "why is the number different from last week" → `forecast-delta-brief`.
- Internal quarterly operating review for the sales or revenue team → `qbr-generator`.
- Customer-facing value or success review → `customer-qbr`.
- Board, investor, fundraise, or other non-operational governance audience → this skill.

If the quarter-anchor gate below fails, keep the safe stop. Do not fall back to a weekly
brief, and do not fall back to a legacy investor-report skill to produce a deck anyway.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its
checklist before any data call: logical tool names, one ToolSearch `select:` batch for
deferred tools, `current_context` first, `scoped_org_id`, live-schema inspection, read-only
discipline, fixture exclusion, unavailable-not-zero, correlational language, one-link
delivery.

Skill-specific gates, stricter than the preflight and run **before any slide is built**:

1. **Tenant.** `current_context` must pass (non-empty `organization.id`, active
   organization and user, approved membership). Store `scoped_org_id` and the organization
   name for the title slide.
2. **ID match.** On the granular `forecast_confidence_decomposition` response, require
   `entity_id` and the organization citation's `object_id` to equal `scoped_org_id` after
   string normalization. On mismatch or absence, stop and report both IDs. Do not
   interpret any number first.
3. **Quarter anchor.** Compute the span from the returned `period.previous_date` to
   `period.current_date`. Require it to fall in the prior comparison quarter and cover
   **75–105 days**. For a declared non-standard fiscal quarter, require the returned anchor
   to match that declared period instead.
4. **Same-day reading.** Require `period.current_date == as_of`, using the tool's
   organization-scoped `as_of` — not the host or session date, which may sit in another
   timezone. Require acceptable citation freshness.
5. **On any gate failure, stop before generating slides.** Deliver a short readiness
   finding in chat naming the history depth available, the anchor actually returned, and
   the anchor required. **Never substitute a seven-day (or one-day) movement in a
   quarterly pack.**
6. **Read-only.** Never request `refresh: true`. Never call write, note, seed, or reset
   capabilities.
7. **Demo label.** If fixture or demo rows cannot be reliably excluded (typically on a
   staging or demo tenant), the pack may be built only to validate this skill, and every
   slide carries exactly: **Demo data — not for customer or commercial decisions**.
   Fixture history never satisfies the quarter-anchor gate for a real board.

## References — read before any call

- [references/connector-preflight.md](references/connector-preflight.md) — the shared
  tenant, schema, fixture, read-only, missing-evidence, correlation, and delivery contract.
- [references/delta-attribution.md](references/delta-attribution.md) — the four-part delta
  contract (level, movement, attribution, limits). Every quarter-over-quarter number in this
  pack obeys it.
- [references/async-envelopes.md](references/async-envelopes.md) —
  `unified_forecast_summary` and, under cache pressure, `segment_performance_summary` and
  `revenue_engine_context` return processing envelopes. An unhandled envelope produces a
  board slide with a blank number. Read it before the first async-capable call.
- [references/currency-and-fx.md](references/currency-and-fx.md) — reporting-currency
  labels, disclosure of excluded or unconverted amounts, constant currency and FX effect.
  Read it before writing any amount on a slide and before building Step 5's currency
  reading; the pack inherits its checklist.

Also read the `pptx` skill's SKILL.md (and its PptxGenJS reference, where installed)
before writing deck code.

## The moment this serves

Serves **RL2 — the board meeting**. Quarterly, 2–4 weeks of prep, 20–40 hours of CRO and
RevOps time — the largest recurring artifact cost in the role.

Boards lose confidence in a CRO before CEOs do. The pack is judged against the last three,
because board members keep the prior decks. Two questions dominate:

> **"You told us last quarter this would be fixed. What's different now?"**

> **"Is this a market problem or an execution problem?"**

The second one is the whole meeting. One is forgivable and one is the CRO's fault, and the
board is asking which. A pack that reports levels without separating structural from
executional patterns leaves the CRO to answer it live, unprepared.

Today: RevOps pulls numbers, the CRO writes narrative, 4–6 revision cycles, numbers move
mid-cycle and slides fall out of sync. Nobody diffs against last quarter's deck.

This skill rebuilds `investor-revenue-report`, which organised a competent metrics deck
around investor metric categories rather than the questions being asked:

- **Segment performance** is the spine of the market-vs-execution answer.
- **Forecast confidence decomposition** supplies "what changed and why" instead of a
  static confidence score.
- **Organization revenue readiness** qualifies how much weight ML-derived figures can
  carry — a pack quoting a model trained on 10 months of data should say so.
- **The `revenue_engine_context` bundle** collapses roughly six granular calls into one,
  with the exceptions documented below.

---

## Step 1 — Scope

Confirm, defaulting silently if the user says "just do it":

- **Period** — default the current fiscal quarter.
- **Comparison quarter** — default the immediately prior fiscal quarter. This is the anchor
  for every delta and must appear on the slides.
- **Company name** — for the title slide.
- **What the board flagged last time** — ask once; it shapes the narrative directly. Do not
  push if the user does not have it.

### The prior-deck limitation — state it up front

The board's dreaded question compares against **the prior pack**, and Summit53 stores no
generated artifacts. This skill compares prior-period *data*, which is not the same thing:
it cannot tell you what was claimed last quarter, only what was true.

Tell the user this in chat at delivery. If they have last quarter's deck, offer a separate
manual claims diff. Never let the pack imply a deck-to-deck comparison it did not perform.

## Step 2 — Run the quarter-anchor gate first

Call `forecast_confidence_decomposition` with an explicit quarter-length `lookback_days`
(normally ~90, or the actual span of the declared comparison quarter). Apply Preflight
gates 2–5 to the response. This response is then the **authoritative delta spine** — do
not call it a second time in Step 3.

### ⚠ Always pass `lookback_days` explicitly — the default is day-over-day

The single most dangerous trap in this skill. Verified live on Staging:

| Call | `lookback_days` | `previous_date` | `delta_pts` |
|---|---|---|---|
| `forecast_confidence_decomposition()` — no args | `null` | 2026-08-06 | **−1.31** |
| `forecast_confidence_decomposition(lookback_days=7)` | 7 | 2026-07-31 | **−9.86** |
| `revenue_engine_context(sections=[…])` — no `lookback_days` | `null` | 2026-08-06 | **−1.31** |
| `revenue_engine_context(…, lookback_days=7)` | 7 | 2026-07-31 | **−9.86** |

**When `lookback_days` is omitted, the tool anchors to the previous daily snapshot** — a
day-over-day delta — while `period.type` still reports `"month"`. The window is not wrong
so much as unlabelled: a caller who omits the parameter gets a one-day movement that reads
like a period movement. The 75–105-day span check is what catches this; never relax it.

The bundle is **not** the problem: it propagates `lookback_days` correctly and returns
figures identical to the granular call. Pass the parameter on whichever path you use.

Then **echo the returned `period.previous_date` → `period.current_date` in the pack**,
never the requested window and never `period.type`. That is the only way a reader can tell
what was actually compared.

## Step 3 — Pull the evidence in one batch

After the gate passes, fire these together so async polls overlap.

### The bundle — one call for breadth

```
revenue_engine_context(
  sections = ["snapshot", "engine_state", "readiness",
              "segment_performance", "forecast_decomposition"],
  persona = "cro",
  fast_forecast = true,
  period_offset = 0,
  lookback_days = <same quarter-length value as the gate call>
)
```

Note `metadata.granular_tools_remain_authoritative: true` — the bundle is a convenience
layer, not the source of record. Where bundle and granular values disagree, the granular
value wins and the disagreement goes in the sources note.

**Bundle warnings are namespaced**: `"segment_performance:no_explicit_segment_field"`,
`"forecast_decomposition:partially_instrumented"`. Split on `:` and route each warning to
the section it belongs to. Do not discard the prefix and do not drop the warning.

### Granular calls alongside the bundle

1. `unified_forecast_summary` with `period_offset: 0`, `detail_level: "detailed"` —
   authoritative current-quarter levels. Async: follow the envelope reference.
2. `unified_forecast_summary` with `period_offset: -1` — prior-quarter levels, for deltas
   the decomposition does not cover. Async: follow the envelope reference.
3. `arr_growth_analytics` (`include_trends`, `include_changes`, `include_benchmarks` all
   true) — ARR, NRR, GRR, logo churn, time-to-value. `include_changes` also returns the
   `constant_currency` block (`delta`, `actual_delta`, `fx_effect`, `status`, `label`,
   `footnote`) and `include_trends` returns `trends.constant_currency` for the trend chart.
   Read `metadata.currency` on this and every revenue response (see the currency reference).
4. `arr_growth_narrative` — read it for a retention insight, then restate the underlying
   numbers yourself. Never paste its text onto a slide: verified live (13 Oct 2026) it used
   `$` in an NZD organization and carried product recommendations ("Deploy Expansion
   Playbooks…"), which do not belong in a board pack.
5. `renewal_forecast_summary` — portfolio-wide renewal bands. Permission-gated; on failure
   fall back to `list_account_contracts` on top accounts **and label the fallback** as a
   top-account inference, never a portfolio forecast.
6. `account_health_movement` — portfolio health trend, correlational wording only.
7. `data_quality_score` — a qualifier on every other number, never a headline. Its
   `issues.accounts_missing_country` and deal-currency-without-rate counts are the coverage
   caveats for the optional regional slide and the FX disclosure.
8. `arr_operating_summary` (optional) — read only `by_dimension.dimension_options` to learn
   whether `sales_region` or `market_region` is `available` for this organization. If
   neither is, or the call is unavailable, skip the regional slide and say so in the
   sources note.

The quota block of `unified_forecast_summary` (current quarter) carries a
`constant_currency` object `{label, attainment_percentage, fx_effect_pts,
spans_fiscal_years, …}` on team and organization rollups. Capture it with the levels.

**Check the scope of the quota and landing figures before using them.** Verified live
(13 Oct 2026): for a connected user whose revenue role is `ic`,
`unified_forecast_summary` returned `quota_metrics` and `projected_landing` for that one
seller (`rep_commit.sellers: 1`, quota NZD 1.23M against an organization quota of
NZD 15.26M in `kpis.pipeline_coverage.quota`), even with `leader_view: "cro"`. When
`quota_metrics.quota_total` does not match the organization quota, or `sellers` is 1,
take target, commit, best case and projection from the `capacity_to_target_planner`
rollup instead, and report organization quota attainment as unavailable on the limits
slide.

**Check that the two quarters are comparable before showing quarter-over-quarter
levels.** Passing the quarter-anchor gate proves the confidence decomposition has 90
days of history; it does not prove the prior-quarter levels are like-for-like. On a demo
or recently imported tenant, close dates can cluster in the current quarter (live: 67 of
67 closed deals in October, prior quarter booked NZD 0.28M vs NZD 6.37M). If the prior
quarter's closed-deal count or pipeline is a small fraction of the current one, do not
present the change as growth: say the quarter split is not like-for-like and keep the
decomposition as the only comparison.

**Do NOT also call `segment_performance_summary`, `organization_revenue_readiness`,
`revenue_engine_snapshot` or `revenue_engine_state`** — the bundle carries them, and a
second copy invites two slightly different numbers on two slides. **One exception:** the
optional regional slide calls `segment_performance_summary(dimension="sales_region" or
"market_region", level="top")`. That is a different cut (region, not segment), so it never
duplicates a bundle number; still do not re-request the default segment view. It requires
analytics permission — on access denial, skip the slide and note the gap.

---

## Step 4 — Three numbers named "confidence"

Live on Staging, simultaneously:

| Source | Field | Value |
|---|---|---|
| `unified_forecast_summary` | `primary.unified_score` | **0.6425** |
| `forecast_confidence_decomposition` | `confidence.current` | **0.508** |
| `revenue_engine_snapshot` (in bundle) | `forecast.confidence_score` | **0.0** |

They measure different things over different windows. A pack that quotes one on the
headline slide and another in the appendix will be caught, and being caught on an internal
inconsistency costs more than the number itself ever could.

**Rule for this skill:**

- Headline confidence = `unified_forecast_summary.primary.unified_score`. It is the
  executive/CRO ensemble view and matches what the leader sees in-product.
- Delta narrative = `forecast_confidence_decomposition`, always labelled with its own band
  and returned window, and explicitly noted as a **separate measure** from the headline.
- `revenue_engine_snapshot.forecast.confidence_score` — **do not put in the pack.** It read
  0.0 against a healthy pipeline; it is an internal input and will not survive a question.

Never present two of these as though they were the same metric at different times.

---

## Step 5 — Market problem or execution problem

The board's second question. `segment_performance` (via the bundle) is what lets you answer
it rather than assert an answer. Start from the server-provided
`pipeline_conversion_mismatches`, then inspect segment win rate with n, coverage, cycle
days, and ACV.

**May read toward *market*:** weakness concentrated in one segment while others hold;
`sales_cycle_days` lengthening across the board; `first_contract_acv` compressing
uniformly; `pipeline_coverage_gap` present in every segment.

**May read toward *execution*:** weakness spread evenly across segments; healthy coverage
converting poorly (`pipeline_conversion_mismatch` signals); win-rate spread across segments
much wider than cycle-time spread; framework/qualification signals dominating
`engine_state.stageStates.pipeline`.

**Currency — the third explanation.** For an organization selling in more than one
currency, part of a quarter's ARR movement can be exchange rates alone. Read
`arr_growth_analytics.constant_currency.status` first:

- `single_currency` — FX is irrelevant; leave currency out of the pack entirely.
- `partial` or `complete` — compare `actual_delta` (reported) with `delta` (constant
  currency at the plan rates named in `label`). When `fx_effect` is material (more than
  about 2% of the reported change, or it flips the sign of growth), the answer to "market
  or execution?" may be "partly neither": say how much of the reported movement is
  currency, then apply the market/execution reading to the constant-currency movement
  only. A `partial` status carries its `footnote` and `excluded_currencies` on the slide.
- No `constant_currency` block — plan rates are not configured; say constant currency is
  unavailable. Never derive it from spot rates.

FX effect is never execution, churn, contraction or a forecast miss. State it plainly as
arithmetic ("currency reduced reported ARR by NZD 180k").

State the strength and uncertainty of the reading. An arithmetic pattern is consistent
with one explanation; it is not causal proof.

**Worked example — the shape of a good finding.** Live: Enterprise win rate 44.4% (n=27)
vs Commercial 68.4% (n=38), with Enterprise carrying *higher* pipeline coverage (3.12x vs
2.73x). More Enterprise pipeline, converting worse. That is not a market-demand story — it
is consistent with an execution or qualification pattern in the Enterprise motion. The
bundle's `pipeline_conversion_mismatches` array flags exactly this case; use it as the
entry point rather than deriving it by hand.

### Segment caveats that must appear in the pack

From live `segment_source` and `caveats`:

- **No explicit segment field is configured.** Segments are resolved from segment
  *territories* — "Enterprise" means "the Enterprise territory", not an account-size
  classification. A board reading it as deal-size segmentation will draw a wrong
  conclusion. State the basis on the slide, in one line.
- **NRR/GRR are nullable per segment** until a segment has enough trailing renewal volume.
  Live: both `renewal_arr` and `expansion_arr` rolled up to **0.0** — segment-level
  retention is not yet computable. Render "not yet computable at segment level", never 0%.
- **Deal size is a separate lens.** Do not merge segment metrics with
  `kpis.*.by_deal_size` bands. They are different cuts and combining them is arithmetic
  nonsense.
- `rollup.win_rate.confidence` came back `"directional"` on n=65. Say "directional" on the
  slide where win rate carries an argument.

---

## Step 6 — Honesty requirements

These are not optional, and they are the part of the pack that earns credibility. Follow
[references/delta-attribution.md](references/delta-attribution.md) for the delta slide:
level, movement, attribution, additivity and residual, uninstrumented drivers rendered as
*not yet measured*, and standing conditions.

### Ramp figures are survivorship-biased

`ramp_cohort` covers only reps **currently inside their ramp window**. Everyone who left
during ramp is excluded. The ramp number Summit53 can produce is therefore biased
optimistic, and a sharp CFO catches exactly this.

Live: **one rep** in ramp, whose `cohort_median_attainment_pct` (3.79%) is identical to
their own attainment because they *are* the cohort.

If a ramp figure appears anywhere in the pack it carries, adjacent to the number, verbatim:

> Ramp figures cover reps currently in their ramp window (n=N) and exclude anyone who
> left during ramp. Read as a best case, not an average.

If n < 3, do not present a cohort median at all. Report the band without naming reps, or
omit the metric. A "median" of one is a number pretending to be a statistic.

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
- **Uninstrumented confidence drivers.** Live: forecast accuracy is `instrumented: false`
  / "building signal" and is invisible to the decomposition.
- **True loss reasons.** Loss reasons are AE-authored; price and timing are structurally
  over-represented in every CRM. A loss-reason chart is a report on what reps wrote down.
- **Model maturity.** From `readiness`: 78 closed deals, 10 months of data. ML-derived
  figures rest on that base — state it once next to the first ML-derived number.
- **Partial-period basis** and **any missing or unavailable source**, with the reason.

A board pack that names its own edges unprompted is more credible than one that doesn't,
and the naming costs one slide.

---

## Step 7 — Partial-period and definition traps

### `arr_growth_analytics.changes` — MTD-matched, still read the basis

Fixed server-side on 8 Aug 2026. `changes` matches the comparison window:

```json
"changes": {"current_period": "2026-08", "previous_period": "2026-07",
            "observed_through": "2026-08-08", "previous_observed_through": "2026-07-08",
            "comparison_basis": "month_to_date_vs_prior_month_to_date",
            "comparison_status": "comparable_partial_periods", "comparable": true,
            "warnings": ["partial_period_mtd_comparison"]}
```

The prior figure dropped from USD 5,250,418 (all of July) to USD 1,640,390 (1–8 July), so the
delta is like-for-like. The old "Total ARR down 100%" artifact is gone.

**Still required of the pack:** render `comparison_basis` and `observed_through` on the
slide. An MTD-vs-MTD comparison over 8 days is a legitimate but small and noisy sample, and
a board reading "down USD 1.6M" without knowing it covers eight days will misread it. Check
`comparable` before using `changes` at all — exclude non-comparable changes — and surface
any entry in `changes.warnings`.

**Empty-window mix is handled server-side.** The mix change entry is suppressed rather than
emitted as a false −100%, and the reason is declared:

```json
"changes": {"warnings": ["partial_period_mtd_comparison", "current_arr_mix_unavailable"],
            "changes": [{"key": "total_arr", …}]}          ← no new_business_pct entry
```

Genuine zero is preserved and distinguishable. Every mix-bearing block carries an
availability triplet:

```json
"arr_mix": {"new_business_pct": 50.4, …,
            "availability": "available", "status": "calculated",
            "evidence": {"denominator_arr": 10419303.26, "opportunity_count": 50}}
```

Present on `arr_mix`, `indexes`, `benchmark_comparison.arr_mix_comparison` and
`gap_to_target`.

**Check `availability` before rendering any mix figure**, and read
`evidence.opportunity_count` before letting a percentage carry an argument — a mix computed
over a handful of deals is arithmetically valid and rhetorically worthless. If
`current_arr_mix_unavailable` appears in `changes.warnings`, say the mix is not computable
for the window rather than leaving the reader to notice a missing row.

Apply the same check to any `trends.points` series — the live series has `total_arr: 0.0`
for six of twelve months, including the current one. Charting it raw draws a line
collapsing to zero. Filter to periods whose `data_quality.confidence_level` is not
`insufficient` before charting, and state how many periods were excluded.

### ARR has three different values too

Live, simultaneously: `total_arr` **USD 10,419,303** (rolling 12-month, by type),
`arr_band.current_arr` **USD 17,242,873** (closed-won base), and
`segment_performance.rollup.active_contract_arr` **USD 27,267,436** (active contract ARR
across segments).

Pick one, define it on the slide, and use it consistently. For a board pack, **active
contract ARR** is usually the right headline (it is what the company actually has under
contract); `total_arr` is a period-scoped flow measure and reads as a much smaller company.
Whichever is chosen, the definition goes on the slide.

**Active contract ARR "at period end" is forward-dated mid-quarter.** With the default
`stock_anchor: "period_end"`, the current-quarter stock is valued at the quarter's last
day (live: NZD 8.08M as of 31 Dec), which drops every contract whose term ends before
then; the prior-quarter stock is as of its own end (NZD 9.64M at 30 Sep). The difference
is renewal exposure, not churn. Lead with the last completed quarter-end figure, show the
period-end figure as "in term through {date}", and point to the renewal book. Never
present the gap as contraction.

### NRR is estimated, and the pack must say so

`nrr.methodology` is `"estimated"` and `nrr.limitations` lists: does not include revenue
contractions, churn based on Closed Lost renewals only, no beginning-of-period baseline.

An NRR of 120.7% that excludes contractions is not comparable to a properly computed NRR,
and "Elite tier" is the tool's label for the value, not a verified standing. Carry the
limitations as a footnote wherever NRR appears. `nrr.confidence` varies by period in the
trend series (`high` / `medium` / `low` / `insufficient`) — do not chart points where it
is `insufficient`.

### Do not render conversion ratios as percentages

`revenue_engine_snapshot.conversion_rates` contains values above 1.0 — live:
`replied_to_pipeline: 3.6667`, `expansion_to_renewed: 2.7`, `working_to_engaged: 1.3469`.

These are **ratios between independently counted stage populations**, not funnel
conversion percentages. A `%` suffix puts "366% conversion" on a board slide. Present them
as ratios with an explicit denominator, or leave them out.
`conversion_rates_by_deal_size.pipeline_to_won` is a genuine rate (all values ≤1) and is
safe.

---

## Step 8 — Build the deck

Build with PptxGenJS following the `pptx` skill. Prefer native PptxGenJS charts (BAR,
DOUGHNUT) over images — editable in PowerPoint, which matters because this deck goes
through 4–6 revision cycles. Write the file to the session's outputs directory as
`Board-Revenue-Pack-{quarter}-{YYYY-MM-DD}.pptx`.

**Design system — Midnight Executive**, unchanged for continuity with decks the board has
already seen: Navy `1E2761`, Ice Blue `CADCFC`, Emerald `10B981`, Amber `F59E0B`, Red
`EF4444`, Charcoal `1E293B`, Off-white `F8FAFC`, Slate `64748B`. Georgia headers 36–44pt,
Calibri body 14–16pt, 16:9, 0.5" margins. Georgia renders with substitute metrics in the
LibreOffice preview, so give header boxes ~10% width slack and do not trust preview fit on
them. Green, amber, and red only where a source band supports that status.

> ⚠ **Set `pptx.layout = "LAYOUT_WIDE"`, not `"LAYOUT_16x9"`.** Both are 16:9, but
> `LAYOUT_16x9` is **10" × 5.625"** while `LAYOUT_WIDE` is **13.33" × 7.5"**. Coordinates
> written for a 13.33" canvas silently render off-slide on `LAYOUT_16x9` — the deck
> generates without error and the right-hand third of every slide is missing. This was hit
> during a test build and only caught by rendering slides to images. Verify by rendering
> and confirming the rightmost element on every slide is visible.

### Slides — 8 (9 with the optional regional view), ordered by the questions

1. **Title** — navy. Organization/company name, "Revenue Review", quarter, comparison
   quarter.
2. **What changed since last quarter** — the delta-with-attribution slide: level, movement,
   contributor table, residual, uninstrumented rows marked *not yet measured*, the returned
   `previous_date → current_date` window. This answers the board's first question and
   belongs **before** the ARR slide.
3. **ARR and retention** — the defined ARR with growth comparison and its basis; NRR and GRR
   paired (a wide gap means expansion is masking churn — call it out in one line); logo
   churn; time-to-value. `data_quality_score` as a corner footnote. When constant-currency
   `status` is not `single_currency` and the FX effect is material, show **reported and
   constant-currency growth side by side** with the FX effect as its own line (a three-row
   bridge: constant-currency movement, FX effect, reported movement), labelled with the
   plan-rate `label`. The ARR trend chart may add the `trends.constant_currency` series
   alongside the reported one, filtered by the same data-quality rule.
4. **Market or execution** — segment table (ARR, win rate + n, coverage, cycle days, ACV),
   the `pipeline_conversion_mismatches` signals, and one explicit sentence naming which way
   the evidence leans and how strongly — market, execution, and (for multi-currency
   organizations with material FX effect) how much of the movement is currency.
   Segment-basis caveat line beneath.
   - **Optional 4b — Revenue by region.** Only when `dimension_options` shows
     `sales_region` or `market_region` available. One table or bar chart from
     `segment_performance_summary(dimension=…, level="top")`: ARR, new ARR, win rate + n,
     coverage per top-level region, **including the Unassigned row** (with
     `accounts_missing_market` where present). Market rows may carry `tam`; never sum a
     parent TAM when any child TAM is missing. Name `dimension_source` in one line. If a
     region trades in several currencies, `metrics.native_by_currency` may show the
     foreign share — never sum native amounts across currencies. Top level only; no rep,
     manager or account names. Skip the slide rather than render a thin one.
5. **Pipeline and forecast** — headline confidence, coverage, quota attainment,
   commit/best-case/pipeline, win rate by deal-size band, ACV drift (flagged only when
   `is_significant: true`). Where the quota `constant_currency` block is present and
   `fx_effect_pts` is material, show **reported and constant-currency attainment** side by
   side with `fx_effect_pts` named as currency, not performance; note `spans_fiscal_years`
   when true.
6. **Renewals and customer health** — renewal bands from `renewal_forecast_summary` (or the
   labelled top-account fallback), logo churn, `account_health_movement` worded as a
   correlational trend.
7. **What we cannot yet answer** — the limits from Step 6, as a slide. Do not bury this in
   an appendix. It is the credibility slide.
8. **Close** — navy, mirrors the title.

If a demo label applies, place it on the slide layout so it appears on every slide.

### Currency on every slide

State the reporting currency once on the title slide (from `metadata.currency`, never
assumed USD). Write every amount with the ISO code or its unambiguous symbol (`NZ$`, `A$`,
`US$`, `€`, `£`); a bare `$` only when the reporting currency is USD and the audience is
US-only. If any deck code formats money (a `formatCurrency`-style helper), pass the
response's currency code into it rather than hard-coding `$`. When `normalization` is
`converted_excluding_unconverted` or the `fx_unconverted_amounts_excluded` warning
appears, put the exclusion beside the affected total ("Excludes €240k in EUR deals with no
rate for Sep 2026") and list it on the limits slide; if it could change a conclusion, call
the conclusion provisional. Never convert an amount yourself.

### Aggregation rule

No rep names, no deal names, no account names in the pack. Segment-, band-, and
portfolio-level only. A board pack that names a rep invites a conversation the CRO does not
want to have in that room. Never write an organization ID, tool prefix, or raw permission
error into the deck; summarise access gaps on the limits slide.

## Step 9 — Verify, then deliver

1. Run the `pptx` skill's `scripts/office/validate.py` on the file and fix every failure in
   the generator.
2. Convert to images (the `pptx` skill's `scripts/office/soffice.py` → PDF → `pdftoppm`)
   and **look at every slide at full size**.
3. Content checks, not exit status. Do not deliver unless:
   - The quarter-anchor gate passed, and the delta slide shows the returned
     `previous_date → current_date` window spanning 75–105 days — not a weekly or daily
     movement.
   - `entity_id` and the citation `object_id` matched `scoped_org_id`, and
     `period.current_date == as_of`.
   - The delta slide carries real contributor values, not blanks from an async envelope
     read as data; contributions sum to the headline within 0.1 pts or the residual is
     shown.
   - Exactly one confidence number appears as the headline, with the decomposition
     labelled as a distinct measure; the snapshot `confidence_score` appears nowhere.
   - One ARR definition is used throughout and defined on the slide.
   - No percentage exceeds 100 where a rate is implied; ratios above 1.0 are shown as
     ratios or omitted.
   - Segment retention cells read "not yet computable", not 0%; every missing value is
     "unavailable" with a reason.
   - Any ramp figure carries the survivorship caveat adjacent to it; no cohort median when
     n < 3.
   - The limits slide is present and non-empty.
   - Reporting currency read from the response and shown once on the title slide; no bare
     `$` unless the reporting currency is USD; no self-computed conversions.
   - Excluded or unconverted amounts are disclosed beside the affected totals.
   - Constant-currency `status` checked; FX discussion omitted for single-currency orgs;
     a material FX effect appears as its own line, never as execution or market
     performance.
   - Any regional slide shows top-level regions with the Unassigned row, no partial TAM
     sum, and no rep, manager or account names.
   - Search the deck text for "caused", "because", "drove", "resulted in". Rewrite each
     unsupported causal claim.
   - The rightmost element is visible on every slide and nothing is clipped, overlapped,
     or wrapped badly.
   - No rep, deal, or account names; no organization ID or tool prefix; no placeholder
     text; the demo label is present on every slide if it applies.
4. Fix and re-verify. Do not declare done until one full fix-and-verify cycle has run. A
   deck that generates without error but has a blank contributor table has failed.
5. Return one clickable link to the PPTX, the prior-deck limitation note, and a short note
   on material evidence gaps and anything excluded.

## Tools

| Tool | Role |
|---|---|
| `current_context` | Tenant gate; `scoped_org_id` and organization name |
| `forecast_confidence_decomposition` | **Authoritative** quarterly delta and attribution — explicit `lookback_days`, gate first |
| `revenue_engine_context` | Bundle: snapshot, engine_state, readiness, segment_performance, forecast_decomposition (cross-check only) |
| `unified_forecast_summary` | Headline confidence and levels, current and prior quarter (async) |
| `get_job` | Async lifecycle |
| `arr_growth_analytics` | ARR, NRR, GRR, logo churn, time-to-value |
| `arr_growth_narrative` | Retention narrative, quoted not paraphrased |
| `renewal_forecast_summary` | Portfolio renewal bands (permission-gated) |
| `list_account_contracts` | Labelled top-account fallback for the above |
| `account_health_movement` | Health trend, correlational wording only |
| `data_quality_score` | Footnote qualifier only; regional and FX coverage caveats |
| `arr_operating_summary` | Optional — `dimension_options` only, to decide whether a regional slide is possible |
| `segment_performance_summary` | Optional regional slide only (`dimension` = `sales_region` or `market_region`, `level="top"`) |
