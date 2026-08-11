---
name: forecast-delta-brief
description: "Create a professional, single-slide, evidence-grounded PowerPoint forecast brief explaining the current number, its movement since the prior weekly reading, and contributor-level attribution. Use for weekly forecast calls, weekly commit reviews, or weekly pipeline reviews when a CRO must answer what changed and why. Do not use for daily or monthly narratives. Route a non-operational board or investor request to board-revenue-pack and an internal quarterly operating review to qbr-generator."
---

# Forecast Delta Brief

Serve the weekly forecast hot seat: **why is the number different from last week?**
Produce a read-only, single-slide executive PPTX that explains movement, not a dashboard
of levels.

## Route and scope

- Use the connected **Summit53** connector by the logical capability names in this
  file. Resolve the actual exposed tool dynamically; never copy an MCP prefix, generated
  hash, or server namespace into the artifact or instructions.
- Use this skill only for a weekly comparison. Set `lookback_days: 7`; do not silently
  adapt it to daily, monthly, quarter-to-date, or quarterly work.
- Route a board or investor request to `$board-revenue-pack`. If its prior-quarter history
  gate cannot pass, preserve the safe stop; do not fall back to a legacy investor skill.
- Route an internal quarterly operating review to `$qbr-generator`.
- Keep the workflow read-only. Never request `refresh: true` or invoke a write capability.

## Read the references

Before calling Summit53, read:

- `references/delta-attribution.md` for the four-part delta contract, additivity,
  instrumentation honesty, and causal-language rules.
- `references/async-envelopes.md` for poll-then-reinvoke handling. A processing envelope
  is lifecycle state, not forecast data.

Then load and follow the available Presentations skill completely for PPTX creation,
speaker notes, rendering, and visual QA.

## 1. Pass the evidence gates

1. Call `current_context`. Require a non-empty `organization.id`, an active organization
   and user, and approved membership. Store that value as `scoped_org_id`; stop if tenant
   scope cannot be verified.
2. Call `forecast_confidence_decomposition` with `lookback_days: 7`.
3. Independently require the decomposition `entity_id` and organization-citation
   `object_id` to equal `scoped_org_id` after string normalization. Also require acceptable
   citation freshness.
   If context, payload, and citation do not agree, stop before interpreting any number.
4. Require non-null `confidence.current`, `confidence.delta_pts`, `period.current_date`,
   `period.previous_date`, and response `as_of`.
5. Require `period.current_date == as_of`. Treat the tool's organization-scoped `as_of`
   as the reconciliation date; do not compare it with the Codex host date, which may be
   in another timezone. If the dates disagree, stop and report both.
6. Use the returned dates, never `period.type`, as the comparison window. If no valid
   prior reading exists, deliver a short readiness finding rather than inventing a delta.

## 2. Pull corroborating evidence concurrently

After the gates pass, request these independent reads together:

1. `unified_forecast_summary` for current `quota_metrics`, pipeline coverage,
   `revenue_at_risk`, and manual commit. Follow the async reference exactly.
2. `risk_heatmap` with `page_size: 50`, ordered by the response's
   `score_semantics.riskiest_first`; paginate until all rows are retrieved.
3. `get_opportunity_signals` for at most three material troubled deals selected from the
   heatmap.
4. `coaching_intervention_plan` only as a corroborating flag, subject to its own
   `coaching_flag_quality` and `ordering` fields.

Do not use `unified_forecast_summary(period_offset: -1)` as last week's value: it is the
prior reporting period, not the prior weekly snapshot. Current level rows therefore have
blank prior and delta cells unless a source returns a genuine same-window comparison.

### Risk-score safeguards

- Drive ordering from `score_semantics`; treat `deprecated_risk_sort_alias` as a hard
  error and reissue the call using `healthScore`.
- Prefer `healthBand` and the canonical factors `frameworkCompleteness`,
  `contactEngagement`, `activityMomentum`, and `repCommitConfidence`.
- Quote a deal only after checking `scoreStatus`, `scoreCalculatedAt`, and age. Label a
  stale score with its age.
- Do not render a deal-level `healthScore` delta unless calculator provenance is exposed
  and reports no legacy rows. Current-state bands may corroborate the decomposition.
- If coaching flag quality is `non_discriminating`, exclude it and quote the warning.
  Never produce an ordinal rep ranking when `ordering.ordinal_ranking` is false.

## 3. Build the delta

Follow `references/delta-attribution.md`:

1. Use `confidence.delta_pts` as the headline; do not recompute it.
2. Sum non-null contributor `contribution_pts` values and compare the result with the
   headline. Render an unexplained residual when its absolute value is at least 0.1 pts.
3. Render uninstrumented contributors as **not yet measured**, never `0.0`.
4. Identify `critical` or `watch` contributors with near-zero movement as standing
   conditions, not causes of this week's change.
5. Carry `partially_instrumented` and other source warnings into the brief.

Deal evidence is corroborative because `risk_heatmap` is current state. Write
"consistent with the execution decline", not "caused the decline". If no deal-level
pattern matches, state that no individual deal explains the movement.

## 4. Render

Save `Forecast-Delta-Brief-{YYYY-MM-DD}.pptx`. Create exactly one 16:9 slide; do not
add a cover, appendix, or closing slide. The default artifact is PPTX. Do not create a
Markdown companion unless the user explicitly requests one.

Use a **Midnight Executive** visual direction: deep navy framing, an off-white editorial
surface, ice-blue structure, and restrained green, amber, or red only where the source
supports that status. Keep the slide scannable from a meeting-room display. Use at least
50 pt for the primary title, 35 pt for section titles where present, 24 pt for subheads,
and 16 pt for body text.

Compose the slide as one executive reading path:

1. **Header** — `Forecast Delta Brief`, the current date, and the exact seven-day
   comparison window.
2. **Hero line** — current confidence, signed headline delta, dominant arithmetic
   contributor, and one concise interpretation sentence containing the exact window.
3. **Movement visual** — a native diverging contribution chart paired with, or replaced
   by when clearer, a compact `Was / Now / Moved / Contribution / Band` table. Show the
   contribution total, any explicit residual, and every uninstrumented contributor as
   **not yet measured**.
4. **Corroboration** — up to three material deals that are consistent with the movement,
   plus any critical or watch standing conditions with near-zero contribution. Keep
   current-state deal evidence visually distinct from arithmetic attribution.
5. **Current-reference strip** — manual commit, pipeline coverage, quota attainment, and
   revenue at risk. Leave prior and delta values blank unless a source supplies a genuine
   same-window comparison.
6. **Visible limits** — a concise, non-empty statement of every limitation that could
   change interpretation, including partial instrumentation, residual, stale scores,
   non-discriminating flags, corroboration-only evidence, and missing sources as
   applicable.

Put the complete provenance in speaker notes, not in a tiny footer. Add a `[Sources]`
block containing every logical capability name used, organization and object identifiers,
as-of timestamps, citation freshness, warnings, residual calculations, excluded evidence,
and async lifecycle notes. Keep the visible slide self-contained for interpretation.

In chat, return only the defensible headline, a clickable link to the PPTX, and a concise
material-gap note when needed. Do not print the slide as Markdown.

## 5. Verify

Do not deliver unless all checks pass:

1. `organization.id`, decomposition `entity_id`, and citation `object_id` all equal
   `scoped_org_id` after string normalization;
   `period.current_date` equals the response `as_of`; and the citation is acceptably fresh.
2. The headline delta is non-null.
3. Contributions add to the headline within 0.1 pts or the residual is explicit.
4. Uninstrumented values are not rendered as zero.
5. The lead sentence contains level, delta, driver, and window.
6. The limits section is present and non-empty.
7. Search for `caused`, `because`, `drove`, `will restore`, and `led to`; rewrite causal
   claims as arithmetic attribution or corroboration.
8. Confirm the final file is a `.pptx` containing exactly one 16:9 slide, with no cover,
   closing slide, placeholder text, or accidental Markdown companion.
9. Render the slide to an image and inspect it at full size. Fix every overlap, clipping,
   line-wrap failure, illegible label, visual imbalance, and source-to-visual mismatch.
10. Run the Presentations skill's `slides_test.py` against the final PPTX and resolve all
    reported errors before delivery.
11. Confirm all body text is at least 16 pt and every interpretation-changing limitation
    is visible on the slide.
12. Inspect the speaker notes and confirm a complete `[Sources]` block is present with the
    logical source names, dates, scope identifiers, warnings, exclusions, and async notes.

## Logical capabilities

| Capability | Role |
|---|---|
| `current_context` | Verify the active organization and citation scope |
| `forecast_confidence_decomposition` | Weekly delta and contributor attribution |
| `unified_forecast_summary` | Authoritative current levels |
| `get_job` | Async lifecycle polling |
| `risk_heatmap` | Current-state deal corroboration |
| `get_opportunity_signals` | First constraint for named deals |
| `coaching_intervention_plan` | Quality-gated rep corroboration |
