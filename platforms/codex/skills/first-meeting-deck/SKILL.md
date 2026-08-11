---
name: first-meeting-deck
description: Create a grounded, customer-facing Summit53 first-meeting or discovery PPTX for a specific account or opportunity, including a visibly quarantined AE prep slide. Use for first calls, discovery meetings, early-stage customer meetings, hypothesis decks, meeting slides, account-specific value conversations, or requests such as "build a deck for my first meeting", "prep slides for this prospect", and "turn this opportunity into a discovery deck". Also use for explicit requests to refresh this skill's Summit53 vendor context or branding references.
---

# First Meeting Deck

Create a conversation deck that earns discovery before it pitches. Ground every prospect claim in live account evidence and every Summit53 claim in verified vendor context.

## Load the specifications

1. Read [references/workflow-spec.md](references/workflow-spec.md) completely before retrieving data, researching, transforming content, or planning slides.
2. Read [references/vendor-context.md](references/vendor-context.md) and [references/vendor-branding.md](references/vendor-branding.md) completely.
3. Use the workflow reference as the authority for research order, transform contracts, audience separation, meeting-length adaptation, slide content, and QA audits.
4. Use the vendor references as the authority for currently documented Summit53 positioning, capabilities, honest boundaries, offer, voice, design tokens, and signature visual.
5. Treat all PptxGenJS, `pptxgenjs.md`, `soffice.py`, `pdftoppm`, Claude, generic `outputs`, and legacy rendering instructions in the references as superseded.
6. Load and follow the available Presentations skill completely for workspace selection, `@oai/artifact-tool` implementation, rendering, tests, visual inspection, and final delivery.

## Validate vendor grounding

- Never use bracketed TODOs, placeholder proof points, unconfirmed reference customers, or expired cohort claims.
- The bundled vendor context was last reviewed on 2026-04-21. Check date-sensitive offer, capability, proof, and cohort claims against a current authoritative source before using them in a deck.
- Do not mutate installed reference files unless the user explicitly asks to refresh the skill. For a refresh request, show the proposed evidence-backed changes and write only after the requested scope is clear.
- A knowledge-base result, battlecard, case study, or public webpage may sharpen a claim only when it remains consistent with verified real capabilities and honest boundaries.

## Resolve live tools and scope

- Use the connected Summit53 MCP/app; discover `list_available_tools` if deployment or namespace is uncertain.
- Discover the exact schema for every named Summit53 tool before calling it. Treat sample arguments in the legacy workflow as semantic guidance only.
- Resolve the account, opportunity, audience, attendees, meeting length, and objective before analysis. Ask only when ambiguity would materially change the deck.
- Parallelize independent Summit53 reads after IDs are known.
- Treat access-guarded revenue signals and optional knowledge matches as enhancements. Missing access must not block the customer-facing deck.
- For fresh prospect or market facts, browse the web with current search/open tools. Prefer the prospect's own website and primary sources; record URLs and dates for traceability.

## Execute

1. Pull existing opportunity narratives, notes, activities, stakeholders, value, discovery, account, and optional knowledge evidence described in the workflow.
2. Research only the bounded fresh-signal categories required for the meeting. Keep verified facts separate from hypotheses.
3. Apply the workflow's transforms to convert internal evidence into invitational customer language.
4. Run the transform-quality and vendor-grounding audits before slide authoring.
5. Preserve the audience boundary:
   - Slide 0 is internal AE preparation, visible and unmistakably labeled `AE PREP · DO NOT PRESENT`.
   - Customer-facing slides must not expose framework scores, risk labels, internal signal confidence, private notes, or AE-only objections.
6. Adapt the customer-facing sequence to the meeting length specified in the workflow. Never pitch before the designated positioning section.
7. Build the PPTX through the Presentations skill and the verified Summit53 branding reference. Use the Figure-Eight visual only when it materially clarifies positioning and fits without crowding.
8. Render and inspect every slide individually at full size. Verify Slide 0 visual quarantine at thumbnail size, audience separation, grounding, meeting-length adaptation, overlap, clipping, wrapping, placeholders, and data/source fidelity.
9. Return one clickable link to the final PPTX plus a concise note on any material evidence gaps or skipped unverified claims.

## Guardrails

- Do not invent capabilities, proof points, customer outcomes, competitor claims, pricing, or implementation commitments.
- Do not name competitors on customer slides unless the user explicitly asks and the evidence is current, relevant, and appropriate.
- Do not present hypotheses as facts or web snippets as CRM evidence.
- Do not hide Slide 0 with PPTX XML or a hidden-slide flag; preserve the visible visual forcing function from the workflow.
- Do not reuse internal planning language in audience-facing copy.
