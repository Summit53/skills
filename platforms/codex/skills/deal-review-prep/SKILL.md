---
name: deal-review-prep
description: Create an evidence-based Summit53 PPTX for a manager-led formal review of one opportunity. Use when a sales manager or revenue leader requests a pipeline-review deck, formal deal-health scorecard, close-readiness review, or coaching artifact. Do not use for an AE's personal inspection cheat sheet (use ae-deal-inspection-prep), a challenged chronology or dark-deal timeline (use deal-timeline-defence), or outreach drafting.
---

# Deal Review Prep

Build a focused review deck from live Summit53 evidence. Keep facts, inferences, and recommended actions visibly distinct.

## Route first

- Use this skill only for a manager-led formal review or PPTX artifact about one deal.
- Route AE-owned self-preparation, likely questions, and answer practice to `$ae-deal-inspection-prep`.
- Route challenged chronology, inactivity-onset, and evidence-trail requests to `$deal-timeline-defence`.
- Route explicit email, note, or rescue-execution requests to `$deal-action-engine` when available; do not execute them here.

## Load the specifications

1. Read [references/workflow-spec.md](references/workflow-spec.md) completely before retrieving data or planning slides.
2. Treat that file as the authority for deal-analysis logic, required evidence, graceful fallbacks, slide content, and the Midnight Executive visual direction—not for discovery or routing.
3. Treat its broad trigger/persona wording, PptxGenJS, `pptxgenjs.md`, `soffice.py`, `pdftoppm`, Claude, and generic `outputs` instructions as legacy notes. Do not follow them.
4. Load and follow the available Presentations skill completely for workspace selection, `@oai/artifact-tool` implementation, rendering, overflow tests, visual QA, and final delivery.

## Resolve live tools

- Use the connected Summit53 MCP/app. If its namespace or availability is uncertain, discover `list_available_tools` first.
- Discover the exact schema for every named Summit53 tool before calling it. Never infer argument names from the legacy workflow.
- Start with the opportunity ID when supplied. Otherwise search by deal/account name and resolve ambiguity before continuing.
- Parallelize independent read calls after the opportunity and account IDs are known.
- Treat staging-only and access-guarded enhancements as optional. Missing access must not block the base deck.

## Execute

1. Resolve the opportunity and scope.
2. Pull the evidence required by the workflow specification, adapting only to tools that are actually available.
3. Record unavailable, empty, stale, or contradictory evidence. Do not convert missing data into a zero or a positive signal.
4. Synthesize the health verdict, first constraint, blockers, activity cadence, coaching questions, and prioritized next actions.
5. Keep tool-provided scores separate from model-derived judgments. Label correlations and inferred risk as such.
6. Build the PPTX with the Presentations skill. Preserve the requested compact deal-review narrative, but change layouts or slide count when needed for legibility.
7. Render and inspect every slide at full size. Fix unintended overlap, clipping, wrapping, unreadable charts, unresolved placeholders, and data mismatches before delivery.
8. Return one clickable link to the final PPTX and a short note about material evidence gaps.

## Guardrails

- Do not send rescue emails or execute recommended actions. `prepare_dark_deal_rescue`, when available, is shadow-mode evidence only.
- Do not reveal access-denied details inside the deck.
- Do not claim causality from activity, framework, account-health, or signal correlations.
- Preserve the source deck's evidence-first coaching posture; do not turn it into a generic sales pitch.
