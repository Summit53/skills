---
name: qbr-generator
description: Create an internal Summit53 quarterly revenue or sales review as an executive PPTX, with an optional DOCX companion. Use for quarterly operating reviews, executive performance decks, and pulling together the quarter's revenue numbers. Despite the legacy name, do not use for a customer-facing QBR; use customer-qbr. Route board or investor reporting to board-revenue-pack.
---

# Quarterly Revenue Review

Turn live revenue evidence into an executive quarterly narrative with decisions, risks, and next-quarter priorities.

## Load the specifications

1. Read [references/workflow-spec.md](references/workflow-spec.md) completely before retrieving data or planning the deck.
2. Use it as the authority for period logic, KPI definitions, narrative synthesis, graceful fallbacks, slide content, and Midnight Executive direction.
3. Ignore its PptxGenJS, `pptxgenjs.md`, Claude, generic `outputs`, and legacy rendering instructions.
4. Load and follow the available Presentations skill completely for PPTX creation and QA.
5. If the user explicitly requests a DOCX companion, also load and follow the available Documents skill. Do not create a DOCX by default.

## Resolve live tools

- Use the connected Summit53 MCP/app; discover `list_available_tools` when the namespace or deployment is uncertain.
- Discover every exact tool schema before calling it. Treat tool names and sample arguments in the legacy workflow as semantic guidance only.
- Resolve the reporting period, team scope, comparison period, currency, and intended audience from the request or available context.
- Parallelize independent read calls. Keep access-gated enhancements optional.

## Execute

1. Establish scope and period; state any unavoidable period assumptions.
2. Pull the required KPI, forecast, risk, activity, retention, and execution evidence.
3. Preserve denominators, sample sizes, timestamps, and data-quality caveats.
4. Synthesize one headline narrative, the most important honest risk, quarter-over-quarter movement, and the few forward decisions that matter.
5. Build the PPTX through the Presentations skill. Favor a coherent executive story over exhaustive dashboard coverage.
6. Render and inspect every slide at full size; fix overlap, clipping, wrapping, chart errors, placeholder content, and source-data mismatches.
7. If requested, create the DOCX companion from the same reconciled figures and verify it with the Documents skill.
8. Return clickable links to the final artifacts plus a concise note on material gaps or excluded access-gated metrics.

## Guardrails

- Route board or investor reporting to `$board-revenue-pack`; do not blend that framing into
  an internal operating QBR.
- Route a customer-facing QBR or value review to `$customer-qbr`.
- Do not hide weak metrics or invent benchmarks.
- Describe health movement, interventions, and execution signals as correlational unless a source proves causation.
- Never expose permission errors, rep-sensitive detail, or unsupported customer claims in audience-facing slides.
