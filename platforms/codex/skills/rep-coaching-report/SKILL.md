---
name: rep-coaching-report
description: Prepare an evidence-based Summit53 routine developmental coaching or recurring 1:1 PPTX using diagnostics, agenda, pipeline, deal risk, activity, qualification, coaching history, and prior actions. Also use when the user explicitly asks to log notes, close a coaching session, or record a later coaching outcome. Trigger on "prep my 1:1 with this rep", "what should I coach them on", coaching-plan follow-up, and explicit post-session capture. Do not use for promotion, PIP, talent calibration, formal performance review, HR documentation, or an employment decision; use rep-evidence-dossier.
---

# Rep Coaching Report

Prepare a humane, evidence-based coaching conversation around one high-leverage thesis. Keep diagnostic evidence separate from judgment about the person.

## Load the specifications

1. Read [references/workflow-spec.md](references/workflow-spec.md) completely before retrieving data or planning slides.
2. Use it as the authority for coaching diagnosis, agenda, pattern analysis, graceful fallbacks, slide content, post-session fields, and Midnight Executive direction.
3. Ignore its PptxGenJS, `pptxgenjs.md`, Claude, generic `outputs`, and legacy rendering instructions.
4. Load and follow the available Presentations skill completely for PPTX implementation, rendering, tests, visual QA, and final delivery.

## Resolve live tools

- Use the connected **Summit53** connector; call `current_context` first and require the intended organization before reading rep evidence.
- Discover the exact schema for every tool before calling it.
- Resolve the rep, coaching period, manager scope, and session before analysis.
- Parallelize independent read calls after identity and scope are known.
- Use `coaching_history` for delivered coaching. Treat generic Intervention Ledger rows as deal-execution accountability only.
- Treat access-gated roster and signal tools as optional.
- Exclude synthetic, `demo_seed`, and `demo_fixture` rows from a real 1:1. A Staging test that uses them must label the deck **Demo data — not for real coaching**.

## Prepare the coaching deck

1. Pull the diagnostic, agenda, prior actions, pipeline, risk, activity, qualification, forecast, and supporting evidence specified in the workflow.
2. Preserve timestamps, comparison windows, targets, benchmarks, sample sizes, and missingness.
3. Form one coaching thesis grounded in the Results/Effort/Knowledge/Skills diagnostic and corroborating evidence.
4. Distinguish facts, model inferences, coaching hypotheses, and agreed actions.
5. Use behavioral, forward-looking language. Avoid identity labels, blame, or unsupported performance conclusions.
6. Build the PPTX through the Presentations skill. Keep the core conversation concise; optional evidence slides may extend the legacy nominal count when necessary.
7. Render and inspect every slide at full size; fix overlap, clipping, wrapping, sensitive-detail leakage, placeholder copy, and source mismatches.
8. Return one clickable link to the final PPTX plus a short note on material evidence gaps.

## Close or log a session

- Perform a write only when the user explicitly asks to save notes, action items, or close the session.
- Use `complete_coaching_session` only to attest and complete a session. Use `record_coaching_outcome` only for a later outcome assessment; never conflate the two lifecycle events.
- Both writes are approval-gated. Inspect the exact schema and current session state, require the user's explicit request and the connector's approval receipt, preserve idempotency, avoid duplicate completion, and report only the confirmed saved result.
- If no write tool is available, produce a structured manager-notes and action-items draft. State clearly that nothing was saved; do not imply completion.

## Guardrails

- Route promotion, PIP, talent calibration, formal performance documentation, and employment decisions to `$rep-evidence-dossier`.
- Do not expose one rep's sensitive evidence to an unauthorized audience.
- Honor `coaching_flag_quality` and `ordering.ordinal_ranking`; never render an ordinal rep rank when ranking is prohibited or the flag is non-discriminating.
- Do not turn correlational activity patterns into causal claims.
- Do not present assigned deal interventions as coaching delivered.
- Do not overwrite or duplicate an already completed session.
- Do not silently drop prior action items or fabricate commitments.
