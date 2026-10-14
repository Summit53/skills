---
name: "renewal-defence-pack"
description: "Prepare an evidence-grounded, read-only renewal defence for one named account and one renewal contract: contract facts, a promise-to-impact evidence table matched only by recorded outcome links, procurement-ready proof points with safe wording, gaps that weaken the defence, and questions to resolve — or an evidence-readiness finding when the records can't support a defence. Use when Customer Success must defend an active renewal, procurement challenge, commercial review, or renewal-risk meeting, e.g. 'build a renewal defence for [account]', 'procurement is pushing back on [customer]'s renewal', 'help me defend this renewal', 'renewal risk meeting prep for [account]', or 'save plan for [customer]'. Do not use for a portfolio renewal forecast or NRR outlook — use cs-renewal-forecast. Do not use for a customer-facing business review — use customer-qbr. Internal quarterly revenue review — use qbr-generator."
metadata:
  version: "1.1.0"
  baselined: "2026-10-13"
  status: "active"
---

# Renewal Defence Pack

Build a concise, read-only defence for one account and one renewal contract. Anchor every
commercial statement to the recorded contract, value promise, or delivered-impact evidence. If
those records do not support a defence, deliver an evidence-readiness finding instead.

## Route first

- Use this skill for one named account renewal or a procurement challenge.
- Portfolio or time-series renewal outlook, NRR question → `cs-renewal-forecast`.
- Customer-facing relationship and outcomes review → `customer-qbr`.
- Internal quarterly revenue review → `qbr-generator`.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its
checklist before any data call. It covers connector and tenant resolution
(`current_context` first), deferred-tool loading
([host-adapters.md](references/host-adapters.md#loading-the-summit53-tools)), live-schema inspection, read-only
discipline, fixture exclusion, unavailable-not-zero, correlational language, and delivery.

Skill-specific gates:

- Read-only: never create or update a contract, value contract, impact entry, opportunity
  note, task, email, or approval-gated action. Never follow suggested write actions in a
  response.
- Demo label (commercial/customer use): inspect fixture, synthetic, seed, source, provenance,
  names, and free-text fields before using a row. Exclude synthetic, `demo_seed`,
  `demo_fixture`, `[DEMO]`, `demo-*`, seeded, generated, or test records from a real customer
  or commercial pack. When the connector or `current_context` identifies a demo, test, or
  staging deployment and payloads do not reliably expose row-level fixture metadata, label
  every output:

  > **Demo data — not for customer or commercial decisions.**

  A tenant whose `current_context` reports `organization.is_demo: true` is always a demo run, in
  every environment: apply the label and follow
  [Demo tenants](references/connector-preflight.md#demo-tenants).

  Do not remove that label when exporting or summarising the pack.

## 1. Confirm tenant and target

1. Call `current_context`. If tenant scope cannot be verified, stop before reading account
   data.
2. Require one unambiguous `account_id`. If the user supplies an account name, call
   `search_accounts` with that query and a small limit. Accept one exact name match only; show
   candidates and ask the user to choose when ambiguity remains.
3. Call `list_account_contracts` with the account ID.
4. Select the user-specified contract when present. Otherwise select the active primary
   contract with the nearest future `end_date`. If multiple plausible renewals remain, show
   their IDs, end dates, ARR, and status and ask the user to choose; do not merge contracts.
5. Stop if the account is absent, no contract exists, or the selected contract has no usable
   renewal date. Report exactly which prerequisite is missing.

Treat `AccountContract.arr` as renewal ARR. Never substitute an opportunity amount for it.
Render every date with its recorded source. When `end_date_source` is `estimated`, label the
date **planning estimate — confirm before commercial use** and never call it a contractual
renewal date.

## 2. Build the promise-to-impact chain

After fixing the account and contract IDs, run the independent reads in parallel:

1. If `source_opportunity_id` is present, call `get_value_contract` with it. If it is absent,
   record that prerequisite gap and do not issue an invalid call (never pass an account or
   contract ID to `get_value_contract`).
2. Call `list_impact_entries` with `account_id` and `contract_id`.
3. Call `get_value_impact_card` with `account_id` and `contract_id`.

Preserve citations, timestamps, warnings, IDs, provenance markers, and missing-data reasons
from each response.

### Evidence gates

- **No contract:** stop. There is no renewal scope to defend.
- **No source opportunity or value contract:** stop before making a procurement-facing value
  case. Deliver a short readiness finding: contract facts available, promised outcomes not
  recorded, impact evidence not yet attributable to a promise.
- **No promised outcomes:** apply the same stop. Business problems or metrics without a
  promised outcome are context, not a promise-to-impact chain.
- **Value-contract mismatch:** require the returned `account_id` and `contract_id` to match the
  selected account and contract. Otherwise stop; a source opportunity alone does not prove the
  value contract belongs to this renewal scope.
- **No impact entries:** mark the result **Partial — delivered-impact evidence missing**. Show
  contract and promise facts only; do not claim realised value.
- **No assessment or value-impact card:** continue only from raw promised outcomes and impact
  entries. Omit fulfilment, readiness, category, and recommendation claims.
- **Citation or identity mismatch:** stop if an account, contract, opportunity, or citation
  conflicts with the selected scope or `scoped_org_id`.

## 3. Write only supportable claims

For each proposed proof point, record:

| Field | Requirement |
|---|---|
| Promise | Exact promised-outcome summary and any recorded metric, target, unit, direction, and time horizon |
| Delivered evidence | Specific impact-entry summary, date, strength, source, and linked outcome ID |
| Coverage | `supported`, `partial`, or `not evidenced` |
| Safe wording | A bounded sentence no stronger than the recorded evidence |
| Source | Logical capability, record ID, and timestamp |

Apply these rules:

- **Match impact entries to promised outcomes only through `linked_outcome_ids`.** Do not
  infer a link from similar wording alone.
- Treat unlinked entries as contextual evidence and label them **not contractually matched**.
- Treat impact-entry `strength` and `source` as provenance, not automatic proof quality.
- Treat the value-impact card as an internal assessment. Its score, category, expansion
  readiness, commentary, or recommendation is not customer proof and must not replace raw
  entries.
- Preserve recorded units and time horizons. Never invent baselines, savings, adoption, ROI,
  percentages, causal explanations, or future outcomes.
- Say "recorded alongside" or "consistent with" when evidence is correlational. **Banned
  words** unless a cited source explicitly establishes the claim: "caused", "because of",
  "drove", "proved", "guarantees".
- Show missing or stale evidence beside the affected claim, not only in a footnote.

## 4. Render the pack

Produce Markdown unless the user requests another format:

```markdown
# Renewal Defence — {account_name}
Contract: **{contract_id}** · Renewal: **{end_date}** · ARR: **{arr}**
Date basis: **{end_date_source; show planning-estimate warning when estimated}**
Evidence as of: **{latest_cited_timestamp}**
{demo label when required}

## The defensible position
{Two or three sentences stating only contract facts and fully supported value.}

## Promise-to-impact evidence
{Promise / target / delivered evidence / date / coverage / source table.}

## Procurement-ready proof points
{At most five bounded claims with their evidence and safe wording.}

## Gaps that weaken the defence
{Missing promises, unmatched entries, stale evidence, weak provenance, or absent metrics.}

## Questions to resolve before the meeting
{Specific evidence questions; no write actions or invented owners.}

---
Sources: {logical capability names, IDs, timestamps, warnings, and provenance exclusions}
```

If the user requests customer-ready wording, keep the same evidence gates and omit internal
scores, risk categories, expansion-readiness labels, and speculative recommendations. If they
request a DOCX, build it with the host's document toolchain
([host-adapters.md](references/host-adapters.md#building-documents)) using the same content and
gates.

## 5. Verify

Do not deliver a defence unless all applicable checks pass:

1. Tenant, account, contract, and opportunity identities reconcile with `scoped_org_id` and
   the selected scope.
2. ARR comes from the selected account contract and the renewal date is recorded; an
   estimated end date carries **planning estimate — confirm before commercial use**.
3. Every realised-value statement maps to a dated impact entry; every matched claim carries a
   recorded `linked_outcome_ids` link.
4. The value-impact card is clearly separated from raw evidence.
5. Partial and stop conditions remain visible.
6. Demo or synthetic evidence is excluded or the exact demo label is prominent.
7. Search for `caused`, `because`, `drove`, `proved`, `guarantees`, and unsupported ROI or
   percentage claims; remove or bound them.
8. Confirm that no write or approval-gated capability was invoked.

## Logical capabilities

| Capability | Role |
|---|---|
| `current_context` | Verify the active organization |
| `search_accounts` | Resolve one exact account when the user supplies a name |
| `list_account_contracts` | Resolve the selected renewal contract, ARR, dates, and source opportunity |
| `get_value_contract` | Read recorded promises for the source opportunity |
| `list_impact_entries` | Read dated delivered-impact evidence for the selected contract |
| `get_value_impact_card` | Optional internal synthesis and evidence-coverage qualifier |
