---
name: "cs-renewal-forecast"
description: "Prepare a read-only Customer Success portfolio renewal outlook for a CS leader: contract ARR due, at-risk exposure, commit and best-case renewal buckets, top surfaced at-risk accounts, account-health movement, and explicit evidence and NRR limits. Use for a 30- to 180-day renewal book, an internal renewal forecast, or an NRR question that must be bounded by available evidence, e.g. 'what's renewing in the next 90 days', 'renewal forecast for my book', 'how much ARR is at risk this quarter', 'CS renewal outlook for the forecast meeting', or 'what will NRR be'. Do not use for one named account's renewal or procurement defence — use renewal-defence-pack. Do not use for a customer-facing review — use customer-qbr. Do not use for weekly pipeline forecast movement — use forecast-delta-brief. Internal operating QBR — use qbr-generator."
version: "1.0.0"
baselined: "2026-10-13"
status: "active"
---

# CS Renewal Forecast

Prepare a portfolio-level renewal outlook without turning a current snapshot into a historical
trend or an NRR calculation. Keep contract ARR, opportunity forecast buckets, and
account-health movement as separate measures with separate source semantics.

## Route first

- Use this skill for a manager-visible portfolio or team renewal book over 30–180 days.
- One named account's procurement or renewal defence → `renewal-defence-pack`.
- Customer-facing outcomes review → `customer-qbr`.
- Internal operational QBR → `qbr-generator`.
- Weekly pipeline-forecast movement → `forecast-delta-brief`.

Keep level, movement, attribution, corroboration, and causality distinct.

**Banned anchor.** The pipeline `forecast_confidence_decomposition` capability is not
renewal-book history and must never be called or used as a prior anchor for this skill.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its
checklist before any data call. It covers connector and tenant resolution
(`current_context` first), deferred-tool loading, live-schema inspection, read-only
discipline (never refresh, seed, create, update, or approve anything), fixture exclusion,
unavailable-not-zero, correlational language, and delivery.

Demo label (commercial/forecast use): inspect fixture, synthetic, seed, source, provenance,
names, owners, and free-text fields. Exclude synthetic, `demo_seed`, `demo_fixture`, `[DEMO]`,
`demo-*`, seeded, generated, and test rows from a real portfolio or commercial decision. When
the connector or `current_context` identifies a demo, test, or staging deployment and payloads
do not expose reliable row-level fixture metadata, label every output:

> **Demo data — not for customer or commercial decisions.**

## 1. Confirm tenant, authority, and window

1. Call `current_context`. Stop if tenant scope cannot be verified.
2. Require a forecast window from 30 through 180 days; default to 90 days. If the user asks
   for a shorter or longer period, explain the supported range rather than silently accepting
   the tool's clamped value.
3. Call `renewal_forecast_summary` with the explicit `window_days`.
4. Stop on `requires_manager_role`, another authorization warning, an unavailable capability,
   or a non-ready/empty response that does not contain an authoritative renewal book.
5. Require `as_of`, `window_days`, `renewal_book_total`, `renewal_book_at_risk`,
   `commit_renewals`, `best_case_renewals`, and `top_accounts`. Preserve source citations and
   all warnings. Confirm the returned `window_days` equals the requested window.

**Two bases, never reconciled.** `renewal_book_total` and `renewal_book_at_risk` use active
primary account-contract ARR. `commit_renewals` and `best_case_renewals` use existing
renewal-opportunity forecast buckets. These are different source measures: do not force them
to reconcile, subtract one from the other as a gap, or replace contract ARR with opportunity
amount.

## 2. Add portfolio movement and account evidence

For at most the five at-risk accounts surfaced by `renewal_forecast_summary`, call
`account_health_movement` separately with that exact `account_id` and a bounded limit. Do not
use the org-wide mover list as if it explained the renewal book.

For those same accounts, call `list_account_contracts`. Select a primary active contract only
when its account, ARR, and renewal/end date reconcile to the forecast row. Then call
`get_value_impact_card` with both the exact `account_id` and reconciled `contract_id`. Run
independent per-account reads in parallel.

If account-health movement is unauthorized, unavailable, or empty while the renewal forecast
is valid, continue as **Partial — current renewal exposure only**, omit movement conclusions,
and show the exact coverage or authorization warning.

Use the responses as follows:

- `renewal_forecast_summary` is the authoritative current renewal exposure and ranked
  at-risk-account view.
- `account_health_movement` supplies persisted current/previous health pairs for the exact
  surfaced renewal account. Describe them as correlational account movement, not as
  renewal-forecast movement or a cause of renewal risk.
- `get_value_impact_card` can qualify fulfilment evidence and readiness for a named top
  account only after its returned contract matches the reconciled contract. It is an internal
  assessment, not direct customer proof.
- The forecast returns at most five ranked at-risk accounts. Label that list
  **top surfaced accounts**, not the complete at-risk population.

If a top account lacks a value-impact card, keep its forecast risk reasons and mark fulfilment
detail unavailable. Do not drop the account or invent evidence.

## 3. Enforce history and NRR gates

The current capability surface does not provide historical renewal-book snapshots. Therefore:

- Never claim that renewal book, at-risk ARR, commit, or best case increased or decreased
  unless the user supplies a prior dated artifact with the same scope, window, and source
  definitions or a future capability returns a genuine prior anchor.
  `forecast_confidence_decomposition` is never that anchor.
- If a prior artifact is supplied, show both as-of dates, verify equal tenant/scope/window and
  metric definitions, and label the comparison user-supplied. Do not interpolate missing
  periods.
- Use `account_health_movement` only when it reports `ready` or `partial` and each row carries
  non-null current and previous snapshot timestamps. Put the exact anchor dates beside every
  movement claim.
- Render `insufficient_history` as missing history, **never zero movement**. If the overall
  status is `insufficient_data`, omit movement conclusions and state the readiness gap.
- Do not derive account-health movement from a point-in-time value-impact card.

This surface also cannot calculate forward NRR by itself. A defensible NRR forecast requires
the starting recurring-revenue base plus renewals, churn, contraction, and expansion on a
consistent basis. Expansion readiness is not expansion ARR. When the user asks "what will NRR
be?", label the result **renewal exposure outlook — not an NRR forecast** and state which NRR
components are unavailable.

## 4. Protect provenance and claim strength

Carry `as_of`, snapshot timestamps, source freshness, warnings, comparison status, account
counts, and insufficient-history counts into the output. Do not strengthen server-provided
risk reasons into causal explanations. Use "flagged for", "moved", or "is consistent with"; do
not use "caused", "because", "drove", or "will renew".

## 5. Render the outlook

Produce Markdown unless the user requests another format:

```markdown
# CS Renewal Forecast — {as_of}
Window: **next {window_days} days** · Scope: **authorized visible renewal book**
{demo label when required}

## The line
{Contract ARR due, contract ARR at risk, at-risk account count, and explicit source basis.}

## Forecast buckets — separate opportunity basis
{Commit and best case, with the basis warning; no forced reconciliation to contract ARR.}

## Top surfaced renewal risks
{At most five accounts: ARR, renewal date, recorded risk reasons, fulfilment detail, evidence limits.}

## Account-health movement
{Down/up/at-risk-next rows with current and previous timestamps, or explicit insufficient history.}

## NRR and history limits
{Unavailable NRR components, absence of renewal-book history, scope/permission/coverage limits.}

## Actions for the forecast meeting
{Evidence questions and read-only decisions; no system writes or invented owners.}

---
Sources: {logical capabilities, as-of dates, snapshot anchors, citations, warnings, exclusions}
```

Optional derived percentages such as `renewal_book_at_risk / renewal_book_total` must show
their formula, use the same contract-ARR basis, and be omitted when the denominator is zero.

## 6. Verify

Do not deliver unless all applicable checks pass:

1. Tenant and authorized visibility are verified; the requested window equals the returned
   window. Do not infer a team or manager scope unless the server returns it explicitly.
2. Contract ARR and opportunity forecast buckets are labelled as different bases and are not
   reconciled or subtracted.
3. Current renewal values are not described as historical movement without a genuine prior
   artifact; `forecast_confidence_decomposition` was not called or used as an anchor.
4. Every account-health movement row has authoritative current and previous timestamps;
   insufficient history is not zero-filled.
5. The top-account list is labelled non-exhaustive and every value-impact qualification is
   sourced.
6. NRR is either supported by all required components or explicitly not computed and labelled
   **renewal exposure outlook — not an NRR forecast**.
7. Demo/synthetic evidence is excluded or the exact demo label is prominent.
8. Search for `caused`, `because`, `drove`, `will renew`, and unsupported increase/decrease
   claims; rewrite them as bounded level, movement, or corroboration statements.
9. Confirm that no write or approval-gated capability was invoked.

## Logical capabilities

| Capability | Role |
|---|---|
| `current_context` | Verify the active organization |
| `renewal_forecast_summary` | Current contract renewal exposure and forecast buckets |
| `account_health_movement` | Persisted, correlational movement for each surfaced renewal account |
| `list_account_contracts` | Reconcile each surfaced account to the exact primary renewal contract |
| `get_value_impact_card` | Optional contract-matched fulfilment qualifier for surfaced accounts |
| `forecast_confidence_decomposition` | **Banned** for this skill — pipeline history, not renewal-book history |
