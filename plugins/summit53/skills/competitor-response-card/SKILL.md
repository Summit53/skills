---
name: "competitor-response-card"
description: "Prepare a concise, read-only, one-screen response card for an AE handling a named competitor or competitive objection in an active Summit53 deal: verified battlecard and reactive-play evidence kept separate from suggested talk track, discovery questions, proof to use, what to avoid, and one safe next action. Use for late-entering competitors and battlecard-backed objection handling, e.g. '[competitor] just showed up in [deal]', 'how do I respond to [competitor] on this deal', 'give me a competitive talk track', 'they said [competitor] is cheaper — what do I say', or 'prep an evidence-grounded response for this active deal'. Do not use for historical or portfolio competitive patterns, recurring loss reasons, or win-rate drivers — use win-loss-analysis."
metadata:
  version: "1.1.0"
  baselined: "2026-10-13"
  status: "active"
---

# Competitor Response Card

Create a one-screen aid for the next customer conversation. Keep sourced facts visibly
separate from suggested language.

## Route first

- Use this skill only for a named competitor in an **active** deal.
- Route historical outcomes, recurring loss reasons, portfolio trends, or win-rate drivers to
  `win-loss-analysis`.

## Set the scope

Confirm the named competitor, the active opportunity or account, and the objection or decision
at stake. Ask one concise question if any of those essentials is missing. Do not infer a
competitor from vague deal language.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its
checklist before any data call. It covers connector and tenant resolution
(`current_context` first), deferred-tool loading, live-schema inspection, read-only
discipline, fixture exclusion, unavailable-not-zero, and delivery.

Skill-specific gates:

1. Call `current_context` before reading deal or knowledge evidence; stop if it fails.
2. Core evidence sources are the read-only capabilities `list_reactive_plays` and
   `get_battlecard`. If useful and available, use `search_opportunities` and
   `get_opportunity` **only** to confirm that the named deal is active and correctly matched.
3. Call the minimum bounded set needed for the named competitor and objection. Never call
   write, send, draft-email, CRM-note, or approval-gated capabilities.
4. If either core capability is unavailable, say which evidence is missing. Continue only with
   clearly labelled user-provided context; otherwise return an evidence-gap card rather than
   competitive claims.
5. Demo label (commercial use): when the connector or `current_context` identifies a demo,
   test, or staging deployment and payloads do not expose reliable row-level fixture metadata,
   put this exact label at the top of every output:
   **Demo data — not for customer or commercial decisions.** Exclude fixture, demo, synthetic,
   test, or seeded records from real customer guidance unless the user is explicitly running a
   test. A tenant whose `current_context` reports `organization.is_demo: true` is always a demo
   run, in every environment: apply the label and follow
   [Demo tenants](references/connector-preflight.md#demo-tenants).

## Exact battlecard match only

`get_battlecard` (argument `competitor_name`) returns up to three text-ranked candidates, not a
guaranteed exact match.

- Accept a candidate only when its title, tags, or structured payload explicitly identifies
  the named competitor.
- If more than one candidate remains plausible, show the candidate titles and ask the user to
  select. Do not combine them.
- Treat no exact candidate as an evidence gap — never fall back to the nearest-ranked card.

## Reactive plays

When the objection supplies a supported `trigger_type`, pass it to `list_reactive_plays`.
That capability has no limit or pagination, so disclose that the response covers the complete
published play list visible to the caller, and filter locally to the named objection.

## No web research unless asked

Do not perform external web research unless the user separately requests it. If requested, use
the available web search and fetch tools, cite each external fact with URL and access date, and
keep external sources distinct from Summit53 evidence (never under **Verified evidence**).

## Apply the evidence gate

Classify every input before writing:

- **Verified evidence** — a relevant, current fact returned by the battlecard or reactive-play
  capability, with its source and effective date or retrieval date.
- **User-provided context** — a deal fact or objection supplied by the user but not
  independently confirmed.
- **Suggested response language** — a draft talk track, question, or next step. Never present
  it as evidence.
- **Unknown** — missing, stale, contradictory, or out-of-scope information.

Use only evidence that matches the named competitor and the active-deal context. Preserve
caveats, dates, confidence fields, and permission limitations. Do not invent product
comparisons, pricing, integrations, customer references, legal claims, roadmap commitments, or
competitor weaknesses.

## Build the one-screen card

Use this order and keep each section short:

1. **Situation** — opportunity, competitor, objection, next interaction, and evidence
   timestamp.
2. **Verified evidence** — two to five source-grounded facts; show `Unknown` instead of
   filling gaps.
3. **Suggested response** — a concise acknowledgement, differentiation, and proof-oriented
   bridge. Label the whole section as suggested language.
4. **Discovery questions** — three to five questions that reveal decision criteria, evidence
   standards, switching costs, and the customer's actual concern.
5. **Proof to use** — only substantiated proof points returned by the evidence sources;
   include any qualification or expiry.
6. **Avoid** — unsupported claims, named-customer disclosure, competitor disparagement,
   confidential intelligence, and promises outside returned evidence.
7. **Next safe action** — one reviewable step for the AE. Do not send, log, or execute it.

Cite each verified fact compactly with the logical capability and returned record or section.
Keep citations out of the suggested-language section unless they substantiate a specific proof
point.

Return the card in chat or Markdown unless the user explicitly requests another format.

## Quality check

Before returning the card:

- [ ] `current_context` passed and any returned IDs match `scoped_org_id`.
- [ ] The opportunity is active and the competitor is an exact battlecard match, or the card
      discloses that the competitor was user asserted.
- [ ] No suggested wording appears under **Verified evidence**.
- [ ] No external web fact appears unless the user asked for web research, and each one is
      cited with URL and access date outside **Verified evidence**.
- [ ] Facts that are stale, ambiguous, unsupported, synthetic, or unrelated to this deal are
      removed.
- [ ] The output fits on one screen and contains no portfolio-level analysis.
- [ ] Material evidence gaps and the as-of date are stated; the demo label is present when
      required.
- [ ] No write, send, note, or approval-gated capability was called.
