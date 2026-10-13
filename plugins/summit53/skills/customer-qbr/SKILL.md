---
name: "customer-qbr"
description: "Prepare a customer-facing Summit53 success and value review grounded only in verified value-contract and impact evidence: agreed outcomes, verified progress, measurement gaps, and mutual next commitments, with a customer-safety gate that strips internal scores, forecasts, and notes. Default output is a customer-safe brief or deck specification; PPTX or DOCX only on explicit request. Use for customer QBRs, executive business reviews (EBRs), value-realisation reviews, outcome progress, and mutual success plans, e.g. 'customer QBR for Acme', 'prep the EBR with [customer]', 'what value have we delivered to [account] this quarter', or 'customer-safe value review'. Do not use for an internal revenue or sales operating QBR — use qbr-generator. Do not use for renewal risk, a save plan, or renewal defence — use renewal-defence-pack. Board or investor pack — use board-revenue-pack."
version: "1.0.0"
baselined: "2026-10-13"
status: "active"
---

# Customer QBR

Prepare a customer-safe account review that proves only what the recorded evidence supports
and ends with mutual next commitments.

## Route first

- Use this skill for an external customer value and success conversation.
- Internal quarterly revenue or sales operating review → `qbr-generator`.
- Renewal-risk case, save plan, or internal renewal defence → `renewal-defence-pack`.
- Board or investor pack → `board-revenue-pack`.

## Set the scope

Confirm the customer account, reporting period, intended customer audience, and requested
deliverable. Ask one concise question if the account or period cannot be resolved safely. Do
not blend contracts, subsidiaries, periods, or currencies without explicit confirmation.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its
checklist before any data call. It covers connector and tenant resolution
(`current_context` first), deferred-tool loading, live-schema inspection, read-only
discipline, fixture exclusion, unavailable-not-zero, correlational language, and delivery.

Skill-specific gates:

1. Call `current_context` before reading customer evidence; stop if it fails.
2. Never call write, note, send, outcome-recording, or approval-gated capabilities.
3. If a required capability is unavailable or access is denied, disclose the gap. Do not
   replace missing evidence with assumptions or internal CRM signals.
4. Demo label (customer-facing use): when the connector or `current_context` identifies a
   demo, test, or staging deployment and payloads do not expose reliable row-level fixture
   metadata, put this exact label at the top of every output:
   **Demo data — not for customer or commercial decisions.** Never present fixture results as
   a real customer's value story.

## Resolve evidence

Use only the read-only evidence needed for the account and period:

- `search_accounts` to resolve an account name when no account ID is supplied;
- `list_account_contracts` to select the correct contract for that account;
- `get_value_contract` with an exact `opportunity_id` for agreed outcomes, measures, owners,
  and target dates;
- `list_impact_entries` for dated value evidence within the review period;
- `get_value_impact_card` with the selected `account_id` and `contract_id` for a reconciled
  summary, never as the sole proof of a customer claim.

**Tool-argument rule for `get_value_contract`.** Never pass an account or contract ID to it,
and never infer an opportunity ID. Use only the selected contract's recorded
`source_opportunity_id`. Require the returned value contract's `account_id` and `contract_id`
to match the selected scope; otherwise mark it unavailable.

## Reconcile the evidence

1. Select the exact matching contract and preserve its status, effective dates, outcome
   identifiers, metric definitions, units, and currency.
2. Filter impact entries to the same account, contract, outcome, and reporting period.
   Deduplicate repeated entries and preserve source, measurement date, status, and confidence.
3. Reconcile impact-card totals and fulfilment summaries to the underlying entries. Disclose
   unexplained differences rather than forcing agreement.
4. Build a claim ledger with: agreed outcome, baseline, target, observed result, measurement
   period, evidence source, verification status, and caveat.
5. Phrase relationships as observed progress. Do not claim that Summit53 caused a business
   result unless the returned evidence explicitly supports that attribution.

**Five-condition claim gate.** A customer-ready value claim requires all of the following:

1. an exact account and contract match;
2. a linked agreed outcome or measure;
3. a dated impact entry in the review period;
4. an explicit value and unit, or a clearly recorded qualitative status;
5. non-demo provenance suitable for customer use.

An aggregate score or narrative without supporting entries is context, not proof.

## Apply the customer-safety gate

Exclude internal health or risk scores, renewal probability, forecast and pipeline details,
sales-rep performance, coaching data, private notes, confidential deal strategy, intervention
records, unsupported benchmarks, and other customers' information.

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
3. **Verified progress** — a small evidence table with baseline, target, observed result,
   period, and caveat.
4. **What the evidence shows** — a neutral narrative that distinguishes achieved, progressing,
   not measured, and blocked outcomes.
5. **Measurement gaps** — what still needs validation, without exposing internal diagnostics.
6. **Next-period commitments** — mutual actions with owner, due date, and success measure only
   when supported or explicitly agreed by the user.
7. **Decision or ask** — the customer decision needed next, if any.

Do not turn the review into a sales pitch or renewal defence. Keep customer-visible wording
factual, collaborative, and free of internal labels.

## Create an artifact only when requested

- **PPTX — explicit request only.** Read the `pptx` skill (its SKILL.md and pptxgenjs.md)
  before writing code, build the deck with PptxGenJS from the reconciled claim ledger, render
  every slide to an image (the `pptx` skill's render flow, or soffice → pdftoppm), inspect
  each at full size, correct every finding, and re-inspect affected slides before delivery.
- **DOCX — explicit request only.** Use the `docx` skill and perform its required QA.
- Otherwise return the customer-safe brief or deck specification in chat or Markdown.

Write file outputs to the session's outputs directory and return one clickable link.

## Final checks

- [ ] Account, contract, reporting period, and as-of date reconfirmed; returned IDs match
      `scoped_org_id` and the selected scope.
- [ ] Currency shown only when an authoritative selected source returns it; otherwise marked
      unavailable.
- [ ] `get_value_contract` was called only with the contract's recorded
      `source_opportunity_id`, and its returned `account_id`/`contract_id` matched.
- [ ] Every external claim traces to an eligible value-contract or impact record and passes
      all five gate conditions.
- [ ] Internal, confidential, synthetic, cross-customer, or unsupported material removed.
- [ ] Unknowns and evidence gaps are visible; the demo label is present when required.
- [ ] The final output is a customer review, not an internal QBR or renewal save plan.
- [ ] No write, note, send, or outcome-recording capability was called.
