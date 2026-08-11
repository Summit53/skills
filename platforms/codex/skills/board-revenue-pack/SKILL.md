---
name: board-revenue-pack
description: "Build an evidence-grounded PPTX revenue pack for a non-operational board, investor update, or fundraising audience, centred on what changed since the prior quarter, why, and whether the pattern is structural or executional. Use for board meetings, investor reporting, or quarterly external-governance narratives. Do not use for a weekly forecast call; use forecast-delta-brief. Do not use for an internal operational QBR; use qbr-generator."
---

# Board Revenue Pack

Build an eight-slide board or investor revenue narrative that answers:

1. What changed since the prior quarter?
2. What arithmetically accounts for the change?
3. Does the evidence point toward a structural market pattern or an execution pattern?

The pack reports evidence and its limits. It does not name reps, deals, or accounts.

## Route and scope

- Use the connected **Summit53** connector by the logical capability names in this file. Resolve the
  exposed tool dynamically; never hard-code an MCP prefix, generated hash, or namespace.
- Route a weekly forecast or commit call to `$forecast-delta-brief`.
- Route an internal operational quarterly review to `$qbr-generator`.
- This workflow is read-only. Never request `refresh: true` or run seed/reset capabilities.

## Read the references

Before calling Summit53, read:

- `references/delta-attribution.md` for the four-part delta contract.
- `references/async-envelopes.md` for poll-then-reinvoke handling.

Also load the available presentation-authoring skill and follow its PPTX generation and
visual-verification instructions.

## 1. Confirm scope and the quarterly evidence spine

1. Call `current_context`. Require a non-empty `organization.id`, an active organization
   and user, and approved membership. Store that value as `scoped_org_id`. Independently
   require the granular decomposition `entity_id` and organization-citation `object_id`
   to equal `scoped_org_id` after string normalization. If unavailable or inconsistent,
   stop.
2. Default to the current fiscal quarter and the immediately prior fiscal quarter.
   Confirm company name. Ask once what the board flagged last time; continue without it
   if the user does not provide it.
3. Call `forecast_confidence_decomposition` with an explicit quarter-length
   `lookback_days` (normally about 90).
4. Calculate the actual span from returned `period.previous_date` to
   `period.current_date`. Require the anchor to fall in the prior comparison quarter and
   normally cover 75–105 days. For a non-standard fiscal quarter, require the returned
   anchor to match that declared period.
5. Require `period.current_date == as_of` and acceptable citation freshness; use the
   organization-scoped `as_of`, not the Codex host date, as the reconciliation date.
6. If history is too shallow, the current reading is stale, or the prior anchor is not a
   genuine quarter comparison, **stop before generating slides**. Deliver a readiness
   finding naming the available depth and required anchor. Never substitute a seven-day
   movement in a quarterly pack.

Fixture or demo-labelled history may be used only to validate this skill on staging. A
result built from it must be visibly labelled **Demo data — not for external reporting**.

### Prior-deck limitation

Summit53 compares prior-period data; it does not know what the previous deck claimed.
Tell the user this at delivery. If the prior deck is available, offer a separate manual
claims diff; never imply one occurred automatically.

## 2. Pull evidence concurrently

Use `revenue_engine_context` for breadth with sections `snapshot`, `engine_state`,
`readiness`, `segment_performance`, and `forecast_decomposition`, persona `cro`,
`fast_forecast: true`, and the same explicit quarter-length `lookback_days`.

In the same batch call:

1. `forecast_confidence_decomposition` with the explicit quarter lookback as the
   authoritative delta spine.
2. `unified_forecast_summary` for the current quarter and prior quarter, detailed, using
   the async reference.
3. `arr_growth_analytics` with trends, changes, and benchmarks enabled.
4. `arr_growth_narrative`; quote it without strengthening its claim.
5. `renewal_forecast_summary`; if permission blocks it, use `list_account_contracts`
   only as a clearly labelled top-account fallback, never a portfolio forecast.
6. `data_quality_score` as a qualifier, not a headline.
7. `account_health_movement` only as a correlational portfolio trend.

Preserve namespaced bundle warnings and route each to its source section. Granular
capabilities remain authoritative when bundle values disagree.

## 3. Maintain metric discipline

### Confidence

- Headline confidence: `unified_forecast_summary.primary.unified_score`.
- Movement narrative: `forecast_confidence_decomposition`, explicitly labelled as a
  separate measure with its own returned window and band.
- Exclude `revenue_engine_snapshot.forecast.confidence_score` from the pack.

Never present different confidence definitions as one time series.

### ARR and partial periods

- Pick one ARR definition, define it on the slide, and use it consistently. Prefer
  active-contract ARR for a board view when available.
- Render `arr_growth_analytics.changes.comparison_basis`, `observed_through`, warnings,
  and `comparable`. Exclude non-comparable changes.
- Check every mix block's `availability` and evidence count before using a percentage.
- Exclude trend periods whose confidence is `insufficient` and disclose how many were
  excluded.
- Present NRR as estimated with its returned methodology and limitations; do not imply
  it includes contractions if it does not.

### Segments and market-versus-execution

Use `segment_performance` from the context bundle. Start with server-provided
`pipeline_conversion_mismatches`, then inspect segment win rate and sample size,
pipeline coverage, cycle length, and ACV.

- Concentrated weakness may be consistent with a structural/segment pattern.
- Broad weakness or healthy coverage converting poorly may be consistent with execution.
- State strength and uncertainty; arithmetic pattern is not causal proof.
- Disclose whether segments are territory-derived rather than explicit account-size
  segments.
- Render nullable segment NRR/GRR as **not yet computable**, never `0%`.
- Keep segment and deal-size cuts separate.

## 4. Apply the honesty gates

- Follow `references/delta-attribution.md`: level, movement, attribution, coverage,
  residual, uninstrumented drivers, and standing conditions.
- If ramp figures appear, state the survivor-cohort limitation adjacent to the number.
  Omit a cohort median when `n < 3`.
- Treat intervention/outcome associations as correlational whenever
  `causal_claim_supported` is false.
- Treat loss reasons as AE-authored CRM labels, not ground truth.
- Put model readiness next to the first ML-derived number.
- Ratios above 1.0 from independently counted stage populations are ratios, not
  conversion percentages.

Keep a visible limits slide. At minimum include prior-data-versus-prior-deck, segment
retention availability, uninstrumented confidence drivers, loss-reason provenance,
model maturity, partial-period basis, and any missing sources.

## 5. Build eight slides

Use a 16:9 wide layout and native editable charts where practical:

1. Title — company, quarter, comparison quarter.
2. What changed — quarterly delta, attribution, instrumentation, residual.
3. ARR and retention — defined ARR, growth comparison, NRR/GRR, churn, time-to-value.
4. Market or execution — segment evidence, sample sizes, caveats, strength of finding.
5. Pipeline and forecast — coverage, quota, commit/best case, deal-size win rate.
6. Renewals and customer health — portfolio bands and correlational movement.
7. What we cannot yet answer — mandatory evidence limits.
8. Close.

Use no rep, deal, or account names. Board material stays portfolio-, segment-, and
band-level.

## 6. Verify visually and substantively

Render every slide to images and inspect all eight. Run at least one fix-and-reverify
cycle. Do not deliver unless:

1. The delta slide uses a genuine quarterly anchor and contains real contributors.
2. Exactly one headline confidence definition is used.
3. No rate is incorrectly displayed above 100%.
4. Unavailable segment retention is not shown as zero.
5. Ramp figures carry the adjacent survivor caveat.
6. The limits slide is present and non-empty.
7. Search for `caused`, `because`, `drove`, and `resulted in`; rewrite unsupported causal
   claims.
8. The rightmost element is visible on every slide and no element is clipped.

## Logical capabilities

| Capability | Role |
|---|---|
| `current_context` | Verify organization scope |
| `forecast_confidence_decomposition` | Authoritative quarterly movement spine |
| `revenue_engine_context` | Breadth bundle |
| `unified_forecast_summary` | Current and prior authoritative levels |
| `get_job` | Async lifecycle |
| `arr_growth_analytics` | ARR and retention metrics |
| `arr_growth_narrative` | Bounded retention narrative |
| `renewal_forecast_summary` | Portfolio renewal bands |
| `list_account_contracts` | Labelled top-account fallback |
| `account_health_movement` | Correlational health trend |
| `data_quality_score` | Data-readiness qualifier |
