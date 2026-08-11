---
name: customer-qbr
description: Prepare a customer-facing Summit53 success and value review grounded in verified value-contract and impact evidence. Use for customer QBRs, executive business reviews, value-realisation reviews, outcome progress, mutual success plans, and customer-safe review briefs or deck specifications. Do not use for an internal revenue or sales operating QBR; route that to qbr-generator. Route renewal-risk defence and save-plan requests to renewal-defence-pack.
---

# Customer QBR

Prepare a customer-safe account review that proves only what the recorded evidence supports and ends with mutual next commitments.

## Set the scope

Confirm the customer account, reporting period, intended customer audience, and requested deliverable. Ask one concise question if the account or period cannot be resolved safely. Do not blend contracts, subsidiaries, periods, or currencies without explicit confirmation.

Keep routing boundaries explicit:

- Use `qbr-generator` for an internal quarterly revenue or sales operating review.
- Use `renewal-defence-pack` for a renewal-risk case, save plan, or internal renewal defence.
- Use this skill for an external customer value and success conversation.

## Resolve capabilities

1. Use the connected **Summit53** connector that reports the intended tenant through
   `current_context`.
2. Discover available capabilities and inspect their exact schemas before calling them. Resolve logical capabilities by name and semantics; never persist a physical hash-suffixed tool name.
3. Call `current_context` before reading customer evidence. Require a non-empty
   `organization.id`, an active organization and user, and approved membership; otherwise
   stop.
4. Use only the read-only evidence needed for the account and period:
   - `search_accounts` to resolve an account name when no account ID is supplied;
   - `list_account_contracts` to select the correct contract for that account;
   - `get_value_contract` with an exact `opportunity_id` for agreed outcomes, measures, owners, and target dates;
   - `list_impact_entries` for dated value evidence within the review period;
   - `get_value_impact_card` with the selected `account_id` and `contract_id` for a reconciled summary, never as the sole proof of a customer claim.
5. Never pass an account or contract ID to `get_value_contract`, and never infer an
   opportunity ID. Use only the selected contract's recorded `source_opportunity_id`. Require
   the returned value contract's `account_id` and `contract_id` to match the selected scope;
   otherwise mark it unavailable.
6. Do not call write, note, send, outcome-recording, or approval-gated capabilities.
7. If a required capability is unavailable or access is denied, disclose the gap. Do not replace missing evidence with assumptions or internal CRM signals.

## Reconcile the evidence

1. Select the exact matching contract and preserve its status, effective dates, outcome identifiers, metric definitions, units, and currency.
2. Filter impact entries to the same account, contract, outcome, and reporting period. Deduplicate repeated entries and preserve source, measurement date, status, and confidence.
3. Reconcile impact-card totals and fulfilment summaries to the underlying entries. Disclose unexplained differences rather than forcing agreement.
4. Build a claim ledger with: agreed outcome, baseline, target, observed result, measurement period, evidence source, verification status, and caveat.
5. Phrase relationships as observed progress. Do not claim that Summit53 caused a business result unless the returned evidence explicitly supports that attribution.

A customer-ready value claim requires all of the following:

- an exact account and contract match;
- a linked agreed outcome or measure;
- a dated impact entry in the review period;
- an explicit value and unit or a clearly recorded qualitative status;
- non-demo provenance suitable for customer use.

An aggregate score or narrative without supporting entries is context, not proof.

## Apply the customer-safety gate

Exclude internal health or risk scores, renewal probability, forecast and pipeline details, sales-rep performance, coaching data, private notes, confidential deal strategy, intervention records, unsupported benchmarks, and other customers' information.

Treat fixture, demo, synthetic, test, or seeded records as non-commercial evidence. When the
connector or `current_context` identifies a demo, test, or staging deployment and payloads do
not expose reliable row-level fixture metadata, put this exact label at the top of every output:
**Demo data — not for customer or commercial decisions.** Do not present fixture results as a
real customer's value story.

If no claim passes the evidence gate, stop the customer-delivery path. Return:

- **Not ready for customer delivery**;
- the missing evidence by outcome;
- an internal preparation checklist; and
- optionally, a claim-free customer meeting agenda labelled as a draft.

Never fill missing baselines, targets, outcomes, dates, or impact values with estimates.

## Prepare the review

Default to a concise customer-safe brief or deck specification with this narrative:

1. **Purpose and period** — the agreed scope and as-of date.
2. **Shared objectives** — the contract outcomes in customer language.
3. **Verified progress** — a small evidence table with baseline, target, observed result, period, and caveat.
4. **What the evidence shows** — a neutral narrative that distinguishes achieved, progressing, not measured, and blocked outcomes.
5. **Measurement gaps** — what still needs validation, without exposing internal diagnostics.
6. **Next-period commitments** — mutual actions with owner, due date, and success measure only when supported or explicitly agreed by the user.
7. **Decision or ask** — the customer decision needed next, if any.

Do not turn the review into a sales pitch or renewal defence. Keep customer-visible wording factual, collaborative, and free of internal labels.

## Create an artifact only when requested

For an explicitly requested PPTX, load and follow the available Presentations skill, build the deck from the reconciled claim ledger, render it, inspect every slide, correct every finding, and re-inspect affected slides before delivery. For an explicitly requested DOCX, use the available Documents skill and perform its required QA. Otherwise return the customer-safe brief or deck specification in chat or Markdown.

## Final checks

- Reconfirm account, contract, reporting period, and as-of date. Show currency only when an
  authoritative selected source returns it; otherwise mark currency unavailable.
- Trace every external claim to an eligible value-contract or impact record.
- Remove internal, confidential, synthetic, cross-customer, or unsupported material.
- Keep unknowns and evidence gaps visible.
- Verify that the final output is a customer review, not an internal QBR or renewal save plan.
