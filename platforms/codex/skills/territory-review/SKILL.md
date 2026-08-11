---
name: territory-review
description: Create a strategic Summit53 territory planning or review PPTX using account, pipeline, health, activity, ARR, capacity, and whitespace evidence. Use for territory reviews, regional or geo performance reviews, territory scorecards, whitespace analysis, prospecting allocation, territory health checks, coverage questions, and territory rebalancing.
---

# Territory Review

Build a decision-ready territory narrative from live evidence, with explicit coverage limitations when territory fields are incomplete.

## Load the specifications

1. Read [references/workflow-spec.md](references/workflow-spec.md) completely before retrieving data or planning slides.
2. Use it as the authority for territory scoring, whitespace logic, recommendation categories, graceful fallbacks, slide content, and Midnight Executive direction.
3. Ignore its PptxGenJS, `pptxgenjs.md`, Claude, generic `outputs`, and legacy rendering instructions.
4. Load and follow the available Presentations skill completely for implementation, rendering, tests, visual QA, and final delivery.

## Resolve live tools

- Use the connected Summit53 MCP/app; discover `list_available_tools` if deployment or namespace is uncertain.
- Discover the exact schema for every tool before calling it.
- Resolve the territory definition before analysis: geography, named accounts, owner book, segment, or another user-defined grouping.
- If the source data has no authoritative territory field, derive groupings only from explicit account attributes and disclose the coverage limitation.
- Parallelize independent read calls. Keep access-gated capacity and forecasting enhancements optional.

## Execute

1. Confirm scope, time window, comparison baseline, currency, and audience.
2. Pull the relevant accounts, opportunities, account health, pipeline risk, activity gaps, ARR, forecast, capacity, and renewal evidence.
3. Reconcile accounts and opportunities to territories; track unassigned and ambiguously assigned records separately.
4. Calculate territory indicators with preserved denominators and sample sizes. Do not compare unlike territories without normalization.
5. Identify whitespace, concentration, engagement gaps, execution risk, and rebalancing options.
6. Separate evidence-backed recommendations from hypotheses that require market or coverage validation.
7. Build the PPTX through the Presentations skill. Adjust the source slide blueprint when the number of territories or data density requires a clearer composition.
8. Render and inspect every slide at full size; fix overlap, clipping, wrapping, chart scales, mislabeled territories, placeholder content, and data mismatches.
9. Return one clickable link to the final PPTX plus a short note on scope and coverage limitations.

## Guardrails

- Do not treat absence of CRM records as proof of market whitespace.
- Do not recommend account reassignment from raw pipeline alone; consider capacity, account potential, renewals, engagement, and ownership constraints.
- Describe account-health and activity relationships as correlational.
- Do not expose rep-sensitive coaching details unless the requested audience is authorized and the detail is necessary.
