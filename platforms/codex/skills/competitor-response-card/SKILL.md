---
name: competitor-response-card
description: Prepare a concise, read-only response card for an AE handling a named competitor or competitive objection in an active Summit53 deal. Use for late-entering competitors, battlecard-backed objection handling, competitive talk tracks, discovery questions, and a safe next-conversation plan. Do not use for portfolio or historical win/loss analysis; route that to win-loss-analysis.
---

# Competitor Response Card

Create a one-screen aid for the next customer conversation. Keep sourced facts visibly separate from suggested language.

## Set the scope

Confirm the named competitor, active opportunity or account, and the objection or decision at stake. Ask one concise question if any of those essentials is missing. Do not infer a competitor from vague deal language.

Use this route only for an active deal. Route requests about historical outcomes, recurring loss reasons, portfolio trends, or win-rate drivers to `win-loss-analysis`.

## Resolve capabilities

1. Use the connected **Summit53** connector that reports the intended tenant through
   `current_context`.
2. Discover available capabilities and inspect their exact schemas before calling them. Resolve logical capabilities by name and semantics; never persist a physical hash-suffixed tool name.
3. Call `current_context` before reading deal or knowledge evidence. Require a non-empty
   `organization.id`, an active organization and user, and approved membership; otherwise
   stop.
4. Use the read-only logical capabilities `list_reactive_plays` and `get_battlecard` as the core evidence sources. If useful and available, use `search_opportunities` and `get_opportunity` only to confirm that the named deal is active and correctly matched.
5. Call the minimum bounded set needed for the named competitor and objection. Do not call write, send, draft-email, CRM-note, or approval-gated capabilities.
6. If either core capability is unavailable, say which evidence is missing. Continue only with clearly labelled user-provided context; otherwise return an evidence-gap card rather than competitive claims.

`get_battlecard` returns up to three text-ranked candidates, not a guaranteed exact match.
Accept a candidate only when its title, tags, or structured payload explicitly identifies the
named competitor. If more than one candidate remains plausible, show the candidate titles and
ask the user to select; do not combine them. Treat no exact candidate as an evidence gap.

When the objection supplies a supported `trigger_type`, pass it to `list_reactive_plays`.
That capability has no limit or pagination, so disclose that the response covers the complete
published play list visible to the caller; filter locally to the named objection.

Do not perform external web research unless the user separately requests it. If requested, cite external sources and keep them distinct from Summit53 evidence.

## Apply the evidence gate

Classify every input before writing:

- **Verified evidence**: a relevant, current fact returned by the battlecard or reactive-play capability, with its source and effective date or retrieval date.
- **User-provided context**: a deal fact or objection supplied by the user but not independently confirmed.
- **Suggested response language**: a draft talk track, question, or next step. Never present it as evidence.
- **Unknown**: missing, stale, contradictory, or out-of-scope information.

Use only evidence that matches the named competitor and the active-deal context. Preserve caveats, dates, confidence fields, and permission limitations. Do not invent product comparisons, pricing, integrations, customer references, legal claims, roadmap commitments, or competitor weaknesses.

Treat fixture, demo, synthetic, test, or seeded records as non-commercial evidence. When the
connector or `current_context` identifies a demo, test, or staging deployment and payloads do
not expose reliable row-level fixture metadata, put this exact label at the top of every output:
**Demo data — not for customer or commercial decisions.** Exclude those records from real
customer guidance unless the user is explicitly running a test.

## Build the one-screen card

Use this order and keep each section short:

1. **Situation** — opportunity, competitor, objection, next interaction, and evidence timestamp.
2. **Verified evidence** — two to five source-grounded facts; show `Unknown` instead of filling gaps.
3. **Suggested response** — a concise acknowledgement, differentiation, and proof-oriented bridge. Label the whole section as suggested language.
4. **Discovery questions** — three to five questions that reveal decision criteria, evidence standards, switching costs, and the customer's actual concern.
5. **Proof to use** — only substantiated proof points returned by the evidence sources; include any qualification or expiry.
6. **Avoid** — unsupported claims, named-customer disclosure, competitor disparagement, confidential intelligence, and promises outside returned evidence.
7. **Next safe action** — one reviewable step for the AE. Do not send, log, or execute it.

Cite each verified fact compactly with the logical capability and returned record or section. Keep citations out of the suggested-language section unless they substantiate a specific proof point.

## Quality check

Before returning the card:

- Confirm the opportunity is active and the competitor is an exact match or disclose that it was user asserted.
- Confirm no suggested wording appears under verified evidence.
- Remove facts that are stale, ambiguous, unsupported, synthetic, or unrelated to this deal.
- Confirm the output fits on one screen and contains no portfolio-level analysis.
- State material evidence gaps and the as-of date.

Return the card in chat or Markdown unless the user explicitly requests another format.
