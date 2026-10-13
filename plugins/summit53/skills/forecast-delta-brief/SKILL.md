---
name: "forecast-delta-brief"
description: "Produce a one-slide 16:9 PPTX forecast delta brief for the weekly forecast or commit call: the current forecast-confidence number, its signed movement over a fixed seven-day window, which contributors arithmetically account for it, up to three corroborating deals, and the limits, plus a five-line chat summary readable on a phone. Read-only; can run on a Monday-morning schedule. Use when a user says 'why is the number different from last week?', 'what moved the forecast this week', 'prep me for the forecast call', 'commit call brief', 'weekly forecast delta', 'forecast confidence dropped, why', or 'explain this week's forecast movement'. Do not use for daily or monthly narratives (not supported). Do not use for a board or investor pack — use board-revenue-pack. Do not use for an internal quarterly operating review — use qbr-generator. Do not use for a renewal-book outlook — use cs-renewal-forecast."
metadata:
  version: "3.1.0"
  baselined: "2026-10-13"
  status: "active"
---

# Forecast Delta Brief

Answer the weekly forecast hot seat — **"Why is the number different from last week?"** —
with exactly one read-only, 16:9 executive PPTX slide that explains movement, not a
dashboard of levels, followed by a five-line chat summary.

## Route first

- Weekly forecast, commit, or pipeline-review movement over the last seven days → this skill.
- Daily, monthly, quarter-to-date, or "since the board meeting" windows → not supported.
  Say so and offer the weekly brief; do not silently change `lookback_days`.
- Board, investor, or fundraise narrative → `board-revenue-pack`. If its prior-quarter
  anchor gate fails, keep that safe stop; do not fall back to this weekly brief or to a
  legacy investor-report skill.
- Internal quarterly operating review → `qbr-generator`.
- Renewal-book outlook for CS leaders → `cs-renewal-forecast`.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its
checklist before any data call: logical tool names, deferred tools loaded in one batch
([host-adapters.md](references/host-adapters.md#loading-the-summit53-tools)), live-schema inspection, read-only discipline, fixture exclusion,
unavailable-not-zero, correlational language, one-link delivery.

### Evidence gates — in this order, before any other call

1. **Tenant.** Call `current_context`. Require a non-empty `organization.id`, an active
   organization and user, and an approved membership. Store `scoped_org_id` and the
   organization name. Stop if tenant scope cannot be verified.
2. **Decomposition.** Call `forecast_confidence_decomposition` with `lookback_days: 7`.
   Always pass it explicitly — when omitted, the tool anchors to the previous daily
   snapshot and returns a one-day delta that reads like a period movement.
3. **ID match.** Require the decomposition `entity_id` and the organization citation's
   `object_id` to equal `scoped_org_id` after string normalization, and require acceptable
   citation freshness. If context, payload, and citation disagree, stop before
   interpreting any number and report both IDs.
4. **Required fields.** Require non-null `confidence.current`, `confidence.delta_pts`,
   `period.current_date`, `period.previous_date`, and response `as_of`.
5. **Same-day reading.** Require `period.current_date == as_of`, using the tool's
   organization-scoped `as_of` — not the host or session date, which may be in another
   timezone. If they disagree, stop and report both.
6. **Window from returned dates.** Report the window as `period.previous_date →
   period.current_date`, never from `period.type` (a `lookback_days: 7` call legitimately
   returns `period.type: "month"`). If the returned span is not seven days, show the actual
   span and name the difference in the limits. If no valid prior reading exists, deliver a
   short readiness finding instead of inventing a delta.

Only after all six pass may any other call run.

**Read-only.** Never request `refresh: true` and never invoke a write, note, or send
capability. **Demo label:** if fixture or demo rows cannot be reliably excluded (typically
on a staging or demo tenant), the slide and the chat summary carry exactly: **Demo data —
not for customer or commercial decisions**.

## References — read before any call

- [references/connector-preflight.md](references/connector-preflight.md) — the shared
  tenant, schema, fixture, read-only, missing-evidence, correlation, and delivery contract.
- [references/delta-attribution.md](references/delta-attribution.md) — the four-part delta
  contract, additivity checking, instrumentation honesty, causal-language rules. **This is
  the skill's spine.**
- [references/async-envelopes.md](references/async-envelopes.md) — `unified_forecast_summary`
  returns a processing envelope on a cold cache. Reading it as data produces a blank
  headline and no error. A processing envelope is lifecycle state, not forecast data.
- [references/currency-and-fx.md](references/currency-and-fx.md) — reporting-currency labels,
  excluded-amount disclosure, constant currency and FX in movement attribution. Read it
  before writing any amount on the slide and before Step 2's FX line.

- [references/host-adapters.md](references/host-adapters.md) — how this host loads tools,
  builds and renders slides, and saves and delivers files. Load the host's presentation
  toolchain per [Building slides](references/host-adapters.md#building-slides) before
  writing slide code.

## The moment this serves

Serves **RL1 — the weekly forecast / commit call**. Weekly, 60–90 minutes, with managers
and RevOps. At quarter-end the CEO and CFO join, which changes the room. This is where the
CRO's own number to the CEO gets assembled, and credibility here is cumulative — a pattern
of unexplained revision ends CRO tenures.

The dreaded question is **not** "what's the number?". The CRO can always produce a number.
It is **"Why is it different from what you told me last week?"** Today that gets answered
by RevOps diffing two snapshots in Excel (2–4 hours weekly), or by the CRO stitching
together verbal manager answers on the way into the room.

This skill produces the defensible account of the delta. If it tells you the level without
telling you what moved it, it has failed at its only job. It rebuilds `revenue-monitor`,
which compared against four weeks prior; the number being defended is the one reported
**seven days ago**, so the window is fixed at seven.

---

## Step 1 — Pull corroborating evidence in one batch

After the gates pass, request these together so the forecast poll overlaps the others:

1. `unified_forecast_summary` — authoritative current levels: `quota_metrics`,
   `kpis.pipeline_coverage`, `revenue_at_risk`, `forecasts.manual.commit`,
   `projected_landing` `{value, basis, closed_won, floored_to_closed_won, fallback_reason,
   rep_commit, weighted_pipeline, window}`, the quota `constant_currency` block
   (`attainment_percentage`, `fx_effect_pts`, `label`) and `metadata.currency`
   (`rates_as_of`, `normalization`, `unconverted_amounts`). **Follow the async reference
   exactly.**

   ⚠ **It cannot give you last week's levels.** It is period-scoped — `period_offset: -1`
   returns the *prior reporting period*, not the prior week. Only
   `forecast_confidence_decomposition` carries a week-over-week comparison. So the levels
   strip renders current values with **blank prior and delta cells**, and the slide says
   why. Never fill them with a period-over-period figure — a mislabelled delta in this
   artifact is the exact failure it exists to prevent.
2. `risk_heatmap` with `page_size: 50`, ordered by the response's
   `score_semantics.riskiest_first` (today `sort_by: "healthScore"`,
   `sort_direction: "asc"`). Read `total` on the first response and paginate until every
   row is retrieved.
3. `get_opportunity_signals` for at most three material troubled deals from the heatmap —
   the first constraint on each, used to name what is actually blocking them.
4. `coaching_intervention_plan` — only as a corroborating flag, gated on its own
   `coaching_flag_quality` and `ordering` fields (below).

Do not pull more than this. The leader has 60 seconds; every extra call is latency against
a deadline.

### `risk_heatmap` score semantics — read them, don't assume them

Fixed server-side on 8 Aug 2026. The response declares its own semantics:

```json
"score_semantics": {"primary_field": "healthScore",
                    "direction": "higher_is_healthier",
                    "riskiest_first": {"sort_by": "healthScore", "sort_direction": "asc"},
                    "deprecated_aliases": {"riskScore": "healthScore"},
                    "source": "stored_snapshot", "freshness_seconds": 300}
```

**Drive the call from `score_semantics.riskiest_first`.** `risk_level: "high"` correctly
returns low-health deals (24 of 72 live). Each row carries `healthBand` (`Low` / `Medium` /
`High`) — prefer it over hand-rolled thresholds.

**Do not use `riskScore`.** The name says risk; the value is health. It survives as a
deprecated alias of `healthScore` and returns identical values, so
`sort_by: "riskScore", sort_direction: "desc"` — which reads as "riskiest first" — returns
the **healthiest** deals. Using it raises a machine-readable warning:

```json
"warnings": ["deprecated_risk_sort_alias"],
"metadata": {"warning_details": [{"code": "deprecated_risk_sort_alias",
  "parameter": "sort_by", "value": "riskScore", "replacement": "healthScore",
  "semantics": "higher_is_healthier",
  "riskiest_first": {"sort_by": "healthScore", "sort_direction": "asc"}}]}
```

**Treat `deprecated_risk_sort_alias` as a hard error.** If it appears, the call used the
wrong field — re-issue with `healthScore` rather than interpreting the result. Verified no
false positive: a `healthScore asc` call returns `warnings: []`.

### ⚠ `healthScore` deltas — suppressed (S53-005 legacy rows)

S53-005 (calculator-path divergence) was fixed and deployed on 8 Aug 2026. Both write paths
now use one canonical engine, so **ongoing** path drift is gone.

One residual reason keeps deal-level score deltas suppressed. At the time of writing, 163
stored scores carry canonical provenance and **79 legacy rows remain**. Each will
step-change once, when the reconciler next writes it — a migration artifact, not a business
movement. Because `calculator_version` is **database-only and not exposed over MCP**, this
skill cannot tell a canonical row from a legacy one. So:

- **Do not render a `healthScore` delta.** The headline delta comes from
  `forecast_confidence_decomposition`, which is unaffected — keep it that way.
- Quote `healthScore` only as a **current-state band** (`healthBand`) when naming deals that
  corroborate the confidence driver, never as "improved" or "deteriorated".
- A deal within ~0.06 of a band boundary may cross it on a legacy→canonical rewrite without
  anything changing. Call such a band marginal.

**Lift this restriction only when** `score_semantics.calculator_version` (or a per-row
`calculatorVersion`) appears *and* reports zero legacy rows. Do **not** lift it because
scores look stable — while only one writer is active, agreeing values prove nothing about
provenance.

### Canonical factor names

`riskFactors` carries canonical higher-is-healthier names alongside legacy aliases, with
semantics in `score_semantics.factor_semantics`:

| Canonical | Legacy alias | Meaning |
|---|---|---|
| `frameworkCompleteness` | — | framework evidence completeness |
| `contactEngagement` | `contactRisk` | stakeholder engagement |
| `activityMomentum` | `activityDrag` | opportunity activity momentum |
| `repCommitConfidence` | `repCommitLevel` | forecast-category commitment confidence |

All four are `higher_is_healthier` on 0.0–1.0. **Use the canonical names.** Legacy keys are
emitted with identical values, so `activityDrag: 1.0` on the healthiest deal still reads as
"maximum drag" — and unlike the sort alias, reading a legacy field raises no warning. Quote
the `meaning` string when a sub-score carries an argument.

### Check `scoreStatus` before quoting a deal

Every row carries `scoreStatus` (`fresh` / `stale`), `scoreCalculatedAt`, `scoreAgeSeconds`
and `scoreRefreshPending`, against a `freshness_seconds: 300` budget.

On an unscheduled environment these are routinely stale — observed at 27,947 s (7.8 h),
roughly 93× the freshness window, with `scoreRefreshPending: false` meaning **nothing is
queued to fix it**. Expect stale scores until the production refresh job is scheduled.

If any quoted deal is `stale`, label it with its age on the slide. Do not call the tool with
`refresh: true` to force freshness — that recomputes and persists scores, which is a write.

### The `coaching_intervention_plan` flag gate

The server classifies its own flag quality. **Read it; do not compute a base rate.**

```json
"coaching_flag_quality": {"classification": "non_discriminating",
  "evaluated_reps": 19, "flagged_reps": 18, "flag_rate": 0.9474,
  "non_discriminating_threshold": 0.75,
  "warning": "The coaching flag applies to at least 75% of evaluated reps and must not
              be used as an ordinal performance ranking."},
"ordering": {"ordinal_ranking": false, "basis": "cohort_then_name"}
```

If `classification` is `non_discriminating`, **drop the coaching corroboration** and quote
the warning in the limits. Naming a rep on a near-universal flag is the kind of thing that
gets repeated in a room and cannot be defended when checked.

Never render a priority rank. `ordering.ordinal_ranking: false` prohibits it, and the
underlying ties are real (three reps at 0.8558, three at 0.6100). Per rep, prefer
`evidence_sufficiency.persistent_needs_coaching` over the raw flag — live it is `false` for
every rep (one observed week against a two-week minimum).

## Step 2 — Build the delta

Follow [references/delta-attribution.md](references/delta-attribution.md) exactly:

1. Use `confidence.delta_pts` as the headline. Do not recompute it.
2. Sum non-null `contribution_pts`; compare to the headline; render the residual
   explicitly if its absolute value is ≥0.1 pts.
3. Render uninstrumented contributors as **not yet measured** — never `0.0`.
4. Flag contributors in a `critical` or `watch` band with ~0 contribution as **standing
   conditions**. They did not move; they are also not fine.
5. Carry `partially_instrumented` and every other source warning into the limits.

### Currency — one line, never a contributor

The decomposition does not instrument exchange rates, so currency movement can only land in
the residual or be misread as a business contributor. Rates are monthly: currency can move
the number week over week only when new rates took effect inside the window. Read
`constant_currency.status` and `metadata.currency` from `unified_forecast_summary`:

- `single_currency`, or no `constant_currency` block → no FX line.
- `rates_as_of` falls inside `previous_date → current_date` (a new rate month started in
  the window) **and** `fx_effect_pts` on attainment is material (more than about 2 pts, or
  it flips attainment across a threshold) → add **one FX attribution line** beneath the
  movement visual: "Currency: attainment at {label} differs by {±fx_effect_pts} pts from
  reported; new {rates_as_of} rates took effect this window." It is its own line — not a
  bar in the contributor chart, not folded into another contributor, and not described as
  execution or a forecast miss. Because no week-ago constant-currency reading exists, do
  not claim how many of this week's points it explains; say the residual may include it.
- Otherwise → no FX line; `fx_effect_pts` is a standing level, not this week's movement.

### Attaching deals to the movement

The decomposition names a driver. The room wants deal names. Bridge them carefully:

- Check whether the top heatmap rows' risk type matches the worsening driver (e.g.
  `execution` worsening ↔ deals with low `activityMomentum` or stage-velocity risk;
  `data_quality` ↔ deals with missing fields).
- Name **at most three deals**, with value, stage, current `healthBand`, freshness, and the
  first constraint from `get_opportunity_signals`.
- Word the link as consistency, not causation: *"consistent with the execution decline"*,
  not *"which caused the decline"*. `risk_heatmap` is current state; it can corroborate the
  direction but cannot prove which deals moved the score.
- If no deal-level pattern matches the driver, **say so**: "No individual deal explains the
  movement; the decline is distributed across the portfolio." That redirects the
  conversation from deal rescue to systemic execution.

## Step 3 — Render exactly one slide

Build with the host's presentation toolchain
([host-adapters.md](references/host-adapters.md#building-slides)). Save
`Forecast-Delta-Brief-{YYYY-MM-DD}.pptx` (the returned `current_date`) where the host keeps
deliverables ([host-adapters.md](references/host-adapters.md#saving-and-delivering-files)).
**Exactly one 16:9 slide** — no cover, appendix, or closing slide, and
no Markdown companion unless the user explicitly asks for one.

- **Canvas:** 16:9 widescreen, 13.33" × 7.5". When building with PptxGenJS (Claude's pptx
  skill), use `LAYOUT_WIDE`, never `LAYOUT_16x9` (see host-adapters).
- **Midnight Executive**: navy `1E2761` framing, off-white `F8FAFC` editorial surface, ice
  blue `CADCFC` structure, charcoal `1E293B` text, slate `64748B` secondary text; emerald
  `10B981`, amber `F59E0B`, red `EF4444` only where a source band supports that status.
- **Font minimums** (readable on a meeting-room display): primary title ≥50 pt, section
  titles ≥35 pt where present, subheads ≥24 pt, body ≥16 pt. If content does not fit, cut
  words or move detail to the speaker notes — never shrink below these and never add a
  second slide.

Compose one reading path, top to bottom:

1. **Header** — `Forecast Delta Brief`, the organization name, the current date, and the
   exact `previous_date → current_date` window.
2. **Hero line** — current confidence, signed headline delta, dominant arithmetic
   contributor, and one interpretation sentence containing the window. This is what the
   leader says in the room; it must be defensible verbatim.
3. **Movement visual** — a native diverging bar chart of `contribution_pts`
   (negatives in a contrasting colour; when building with PptxGenJS (Claude's pptx skill),
   use `invertedColors`), paired with or replaced by a compact
   `Was / Now / Moved / Contribution / Band` table when clearer. Show the total and any
   explicit residual. **Exclude uninstrumented contributors from the chart data** — a null
   plots as a zero-length bar — and list them beneath as **not yet measured**.
4. **Corroboration** — up to three deals consistent with the movement (or the "no
   individual deal" statement), plus any standing conditions. Keep current-state deal
   evidence visually distinct from arithmetic attribution.
5. **Current-reference strip** — projected landing, manual commit, pipeline coverage,
   quota attainment, revenue at risk. Prior and delta blank, with "weekly prior not
   available from this source". The projected landing cell carries its basis in plain
   words — "reps' commit roll-up" or "weighted pipeline (fallback)" — and the
   `fallback_reason` goes on the slide if it fits at ≥16 pt, otherwise in the speaker
   notes. Every amount carries the reporting currency code or unambiguous symbol (`NZ$`,
   `A$`, `US$`, `€`, `£`) read from `metadata.currency`; any formatting helper in the slide
   code takes that code rather than a hard-coded `$`.
6. **Visible limits** — concise and non-empty: every limitation that could change
   interpretation (below).

### The limits are mandatory and visible

Include each that applies, on the slide:

- **Uninstrumented drivers** — e.g. forecast accuracy "building signal", so movement in it
  is invisible to this decomposition.
- **Deal attribution is corroborative** — heatmap is current state, not a week-ago
  comparison.
- **Residual** — "X of the Y-point move is not attributed to any instrumented driver."
- **Stale scores** — quoted deals older than the freshness budget, with age.
- **Coaching flag excluded** — "fired on N of M reps and is not discriminating."
- **Missing sources** — any async note or unavailable source, summarised (no raw errors).
- **Window** — if the returned span is not seven days.
- **Excluded currency amounts** — when `normalization` is `converted_excluding_unconverted`
  or `fx_unconverted_amounts_excluded` appears: "Commit and pipeline exclude €240k in EUR
  deals with no rate for Sep 2026." Never convert them yourself.

A leader who knows the edge of the artifact can defend the middle of it. One who discovers
the edge in the room cannot.

### Speaker notes — `[Sources]`

Put full provenance in the slide's speaker notes, not a tiny footer. Begin with a `[Sources]`
block listing: organization name; `scoped_org_id` and the matched `entity_id` / citation
`object_id` (speaker notes only — never on the visible slide); every logical capability
name used (no tool prefixes); `as_of` and window dates; reporting currency, `rates_as_of`
and any `unconverted_amounts` by currency; `projected_landing.basis`, `fallback_reason`
and `floored_to_closed_won`; citation freshness; score ages;
warnings verbatim; the residual calculation; excluded evidence (coaching flag, stale or
fixture rows); and async lifecycle notes.

## Step 4 — Verify before delivering

Check content, not exit status. Do not deliver unless all fifteen pass:

1. `organization.id`, decomposition `entity_id`, and citation `object_id` all equal
   `scoped_org_id`; `period.current_date == as_of`; the citation is acceptably fresh.
2. The headline delta is present and non-null (or a readiness finding was delivered instead
   of a slide).
3. Contributions sum to the headline within 0.1 pts, or the residual is explicit.
4. Every uninstrumented contributor reads *not yet measured*, never 0.0, and is not plotted.
5. The hero line contains level, delta, driver, and the window dates.
6. The visible limits are present and non-empty.
7. Search the text for "caused", "because", "drove", "will restore", "led to"; rewrite each
   as arithmetic attribution or corroboration.
8. The file is a `.pptx` with exactly one 16:9 slide — no cover, closing slide, placeholder
   text, or accidental Markdown companion.
9. The slide is rendered to an image with the host's render step
   ([host-adapters.md](references/host-adapters.md#rendering-and-inspecting-slides)) and
   inspected at full size; every overlap, clipping, wrap failure, illegible label,
   imbalance, and source-to-visual mismatch is fixed; the rightmost element is visible.
10. The host's presentation validation passes on the final file
    ([host-adapters.md](references/host-adapters.md#rendering-and-inspecting-slides)).
11. All body text is ≥16 pt and every interpretation-changing limitation is on the slide.
12. Speaker notes contain the complete `[Sources]` block; no organization ID or tool prefix
    appears on the visible slide; no `healthScore` delta or rep rank appears anywhere.
13. Reporting currency read from the response and shown once; no bare `$` unless it is
    USD; excluded or unconverted amounts disclosed beside the affected level; no
    self-computed conversions.
14. Constant-currency `status` checked; any FX effect appears as its own line (only when
    new rates took effect in the window and the effect is material), never as a
    contributor bar or as performance; omitted for single-currency orgs.
15. Projected landing shows its value with `basis`, and any `fallback_reason` is on the
    slide or in the speaker notes.

## Step 5 — Deliver

Return one clickable link to the PPTX, then a chat summary of **at most five lines** so the
read-on-a-phone-walking-into-the-room use case survives:

```
Forecast confidence {current} ({±delta_pts} pts, {previous_date} → {current_date})
Top contributor: {label} {±contribution_pts} pts{; residual X pts if shown}
Deals consistent with it: {≤3 names} | or: no individual deal explains it
Limits: {the one most interpretation-changing limit}
{Demo label, if it applies}
```

Do not print the slide as Markdown, and do not paste tables into chat.

---

## Scheduling

Where the host supports scheduled runs, run it the morning of the forecast call — the brief
is about the last seven days, so it must be fresh.

```
cron: "0 7 * * 1"   # Mondays 7am, adjust to the call
```

Prompt: *"Run the forecast delta brief for {organization name} with the fixed seven-day
window. Produce the one-slide PPTX and post the five-line summary with the link. Include
the visible limits."*

The scheduled run applies the same gates in the same order. If any gate fails, it posts the
readiness finding (what failed, both values) instead of a slide — it never posts a brief
built on a mismatched tenant, a stale `as_of`, or a non-weekly window. If more than one
Summit53 connector is attached, the scheduled prompt must name the organization so the
preflight can pick the connector without asking.

Unlike the skill it replaces, this one writes nothing back to the CRM — no note-writing
step, no deduplication, no approval gate.

## Tools

| Tool | Role |
|---|---|
| `current_context` | Tenant gate — called first |
| `forecast_confidence_decomposition` | Weekly delta and contributor attribution — **core**, `lookback_days: 7` |
| `unified_forecast_summary` | Authoritative current levels, projected landing and constant-currency attainment (async — follow the envelope reference) |
| `get_job` | Async lifecycle for the above |
| `risk_heatmap` | Current-state deal corroboration (paginate; `healthScore`, never `riskScore`) |
| `get_opportunity_signals` | First constraint per named deal |
| `coaching_intervention_plan` | Rep flag — gated on `coaching_flag_quality` and `ordering` |
