# Currency and FX — Canonical Handling

**Canonical file. Version 1.0.0 · 2026-10-13.**

Maintained once and copied byte-identical into every consuming skill. Bump the version on
edit and re-copy with `tools/sync_canonical_references.py --write`. If two copies
disagree, the higher version wins.

Consumers: `board-revenue-pack`, `qbr-generator`, `forecast-delta-brief`,
`cs-renewal-forecast`, `territory-review`, `win-loss-analysis`,
`revenue-action-brief-s53`.

## Contents

- [Why this exists](#why-this-exists)
- [1. Label every amount with the reporting currency](#1-label-every-amount-with-the-reporting-currency)
- [2. Read the currency metadata on every revenue response](#2-read-the-currency-metadata-on-every-revenue-response)
- [3. Disclose excluded and unconverted amounts](#3-disclose-excluded-and-unconverted-amounts)
- [4. Constant currency and FX effect](#4-constant-currency-and-fx-effect)
- [5. FX in movement attribution](#5-fx-in-movement-attribution)
- [6. Native amounts by currency](#6-native-amounts-by-currency)
- [Checklist](#checklist)

## Why this exists

Summit53 converts deals, contracts and quotas into the organization's **reporting
currency** using monthly rates. Three failures follow when a skill ignores that:

1. **Wrong symbol.** Writing `$` for an NZD, AUD, GBP or EUR organization.
2. **Silent exclusions.** Amounts in a currency with no rate for the period are left out
   of totals. A total that excludes them, presented without comment, understates the
   business.
3. **Currency movement read as performance.** A stronger reporting currency shrinks
   foreign ARR without any change in customers. Calling that churn or a sales miss is
   wrong.

## 1. Label every amount with the reporting currency

- Read the currency from the response: `metadata.currency` (code and normalization) on
  revenue tools, or a top-level `currency` field where a tool returns one (for example
  `account_intelligence_summary`). Do not assume USD.
- Write amounts with the ISO code or its unambiguous symbol (`NZ$1.2M`, `A$`, `US$`,
  `€`, `£`). Use a bare `$` only when the reporting currency is USD **and** the audience
  is US-only.
- State the reporting currency once in the artifact header or sources block.
- Never add amounts from two responses that report different currencies.

## 2. Read the currency metadata on every revenue response

Revenue tools return a `metadata.currency` block. Fields that matter:

| Field | Meaning |
|---|---|
| `amounts_converted` | `true` when any amount was converted from another currency |
| `normalization` | `converted_to_reporting_currency` (complete) or `converted_excluding_unconverted` (some amounts left out) |
| `conversion_method` / `conversion_methods` | How rates were chosen (for example the org's FX policy) |
| `rates_used`, `rates_as_of` | Rates applied and their effective month |
| `unconverted_amounts` | Native amounts by currency that had no rate |
| `excluded_from_totals` | Whether those amounts are missing from the totals |

A `fx_unconverted_amounts_excluded` warning means totals are incomplete.

## 3. Disclose excluded and unconverted amounts

When `normalization` is `converted_excluding_unconverted`, or the
`fx_unconverted_amounts_excluded` warning is present:

- Say so next to the affected total, not only in an appendix: "Excludes €240k in EUR
  deals with no rate for Sep 2026."
- List the excluded native amounts by currency from `unconverted_amounts`.
- Do not estimate a conversion yourself. Missing rates are an administrator fix in
  Revenue Settings, not a number to invent.
- If the excluded share could change a conclusion (for example a region ranking or a
  quota attainment threshold), say the conclusion is provisional.

## 4. Constant currency and FX effect

Constant currency restates actuals at the organization's **plan rates** for a fiscal year,
so period-over-period movement reflects the business rather than exchange rates.

Where it comes from:

- `arr_growth_analytics` with `include_changes: true` returns `constant_currency`
  `{plan_fiscal_year, label, current, previous, delta, actual_delta, fx_effect,
  excluded_currencies, status, footnote}`. `delta` is the constant-currency change;
  `actual_delta` is the reported change; `fx_effect` is the difference.
- `arr_growth_analytics` with `include_trends: true` returns
  `trends.constant_currency` and per-point `trends.points[].constant_currency`.
- `unified_forecast_summary` returns quota `constant_currency`
  `{plan_fiscal_year, label, quota_total, actual_total, attainment_percentage,
  fx_effect_pts, spans_fiscal_years}` on team and organization rollups.

How to use it:

- Read `status` first. `single_currency` means FX is irrelevant: omit the FX discussion.
  `partial` means some currencies lack plan rates: show constant currency with its
  `footnote` and `excluded_currencies`. `complete` means show it without caveat.
- When `fx_effect` is material (more than about 2% of the reported change, or it flips
  the sign of growth), show reported and constant-currency figures side by side and name
  the FX effect explicitly.
- Use the response `label` (for example "FY2027 plan rates") when naming the basis.
- If `spans_fiscal_years` is true, say the period straddles two plan-rate years.
- If plan rates are not configured (no `constant_currency` block), say constant
  currency is unavailable. Do not derive it from spot rates.

## 5. FX in movement attribution

FX effect is a **structural** contributor, like a change in territory assignment. It is
not execution.

- Attribute reported movement as: constant-currency movement (business) plus FX effect
  (currency). Present the FX effect as its own line in any movement waterfall or
  attribution table.
- Never describe FX effect as churn, contraction, expansion, a forecast miss, or rep or
  team performance.
- Use non-causal wording for the business part as usual; the FX part is arithmetic and
  can be stated plainly ("currency reduced reported ARR by NZ$180k").

## 6. Native amounts by currency

Segment, region and ARR operating rows can carry `metrics.native_by_currency`
`{CODE: {new_arr, pipeline_value, active_contract_arr_as_of, …, reporting: {…}}}`.

- Use it when a region or segment trades in more than one currency, to show what
  share of a converted figure is foreign.
- Do not sum native amounts across currencies.

## Checklist

- [ ] Reporting currency read from the response and shown once in the header
- [ ] No bare `$` unless the reporting currency is USD
- [ ] Excluded or unconverted amounts disclosed beside the affected totals
- [ ] Constant-currency `status` checked; FX discussion omitted for single-currency orgs
- [ ] Material FX effect shown as its own line, never as performance
- [ ] No self-computed conversions
