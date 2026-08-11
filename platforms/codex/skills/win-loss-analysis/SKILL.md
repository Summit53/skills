---
name: win-loss-analysis
description: Analyse Summit53 closed-deal outcomes and create a polished win/loss PPTX showing outcome rates, framework and activity patterns, qualitative themes, loss reasons, segment differences, and recommended tests. Use for win/loss reports, win-rate analysis, closed-deal analysis, deal post-mortems, "why are we losing", "what predicts a win", and requests to improve close rate or sales execution using historical deal evidence.
---

# Win/Loss Analysis

Build an evidence-led outcome analysis that distinguishes observed associations from causal explanations.

## Load the specifications

1. Read [references/workflow-spec.md](references/workflow-spec.md) completely before retrieving data or planning slides.
2. Use it as the authority for cohort construction, framework comparisons, qualitative coding, activity analysis, graceful fallbacks, slide content, and Midnight Executive direction.
3. Ignore its PptxGenJS, `pptxgenjs.md`, Claude, generic `outputs`, and legacy rendering instructions.
4. Load and follow the available Presentations skill completely for implementation, rendering, tests, visual QA, and delivery.

## Resolve live tools

- Use the connected Summit53 MCP/app; discover `list_available_tools` if deployment or namespace is uncertain.
- Discover the exact schema for every tool before calling it.
- Resolve the closed-deal period, stages, currency, segment filters, and comparison cohorts before analysis.
- Retrieve bounded result pages until the intended cohort is complete or disclose truncation.
- Parallelize opportunity-level reads in controlled batches.

## Execute

1. Construct reproducible won and lost cohorts. Exclude open, duplicate, deleted, or incomparable records.
2. Preserve cohort sizes, denominators, missingness, comparison windows, and the definition of every calculated rate.
3. Reconcile framework, activity, account, notes, stakeholder, risk, and deal-size evidence at the opportunity level before aggregation.
4. Compare like with like. Segment results when deal size, motion, region, tenure, or stage history would otherwise confound the blended result.
5. Code qualitative themes consistently and show how many deals support each theme.
6. Phrase findings as associations unless the underlying evidence supports causality. Convert recommendations into measurable validation tests.
7. Build the PPTX through the Presentations skill, using editable native charts where appropriate.
8. Render and inspect every slide at full size; fix overlap, clipping, wrapping, misleading scales, small-sample overstatement, placeholder content, and source mismatches.
9. Return one clickable link to the final PPTX plus a short note on cohort scope and limitations.

## Guardrails

- Never call a correlation a predictor without out-of-sample validation.
- Never hide small denominators behind percentages.
- Do not infer a loss reason from an empty field; label unknown explicitly.
- Do not compare framework scores that were captured at materially different deal stages without noting the bias.
- Do not include sensitive verbatim notes when a paraphrased theme is sufficient.
