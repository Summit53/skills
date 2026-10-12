# Connector Preflight — Canonical Contract

**Canonical file. Version 1.0.0 · 2026-10-13.**

Maintained once and copied byte-identical into every consuming skill. Bump the version on
edit and re-copy with `tools/sync_canonical_references.py --write`. If two copies
disagree, the higher version wins.

Consumers: every package under `platforms/claude/skills/`.

## Contents

- [Why this exists](#why-this-exists)
- [1. Resolve the connector and tenant](#1-resolve-the-connector-and-tenant)
- [2. Discover capabilities before calling them](#2-discover-capabilities-before-calling-them)
- [3. Stay read-only unless the skill says otherwise](#3-stay-read-only-unless-the-skill-says-otherwise)
- [4. Exclude fixture and demo records](#4-exclude-fixture-and-demo-records)
- [5. Missing evidence is unavailable, never zero](#5-missing-evidence-is-unavailable-never-zero)
- [6. Correlational language](#6-correlational-language)
- [7. Delivery](#7-delivery)
- [Preflight checklist](#preflight-checklist)

## Why this exists

Every Summit53 skill reads a customer's own revenue data through the Summit53 Revenue
Engine connector. Three failures recur across skills when the preflight is skipped:

1. **Wrong tenant.** A workspace can have more than one Summit53 connector attached (for
   example a production connector and a staging connector, each exposed under a different
   tool prefix). A skill that calls whichever tool appears first can silently report one
   organization's numbers to another organization's leader.
2. **Fixture data presented as fact.** Staging and demo tenants contain seeded records
   that look realistic. A board deck, a renewal defence, or an employment dossier built
   on fixtures is worse than no artifact.
3. **Silence rendered as health.** An unavailable tool, an access-gated field, or an
   empty list rendered as `0`, "no risk", or a green status.

This contract runs before any skill-specific logic. A skill may add stricter gates; it may
not relax these.

## 1. Resolve the connector and tenant

1. Identify the Summit53 connector(s) available in the session. Tool names are exposed
   under a server prefix that differs per installation (for example
   `mcp__summit53__current_context` or `mcp__<uuid>__current_context`). Refer to tools
   by their **logical name** (`current_context`, `risk_heatmap`, …) and resolve the prefix
   at runtime. Never write a prefix, hash, or organization ID into an artifact.
2. If the tools are deferred (listed by name only), load their schemas before calling
   them. In Claude Code, use one ToolSearch call with a `select:` list naming every tool
   the skill needs, rather than loading tools one at a time.
3. Call `current_context` **first**, before any data read. Require:
   - a non-empty `organization.id`;
   - an active organization and an active user;
   - an approved membership.

   Store the organization ID as `scoped_org_id` and the organization name for the
   artifact header. If any requirement fails, stop and tell the user what is missing.
4. If more than one Summit53 connector is attached, call `current_context` on each and
   pick the one whose organization matches the user's request. If the request does not
   say which organization and the connectors disagree, ask one short question naming the
   organizations found. Never merge data across connectors.
5. Where a response carries an organization, entity, or citation object ID, require it to
   equal `scoped_org_id` after string normalization. On mismatch, stop before
   interpreting any number and report both IDs.

## 2. Discover capabilities before calling them

1. Call `list_available_tools` when the connector, deployment, or tool set is uncertain,
   and before relying on any optional capability.
2. Inspect the live schema of every tool before the first call. Tool names and sample
   arguments in a skill are **semantic guidance**: if the live schema renames a parameter,
   changes a scalar to an array, or drops a filter, follow the live schema and note the
   difference in the run summary.
3. Never invent a filter a schema does not offer. If a tool has no owner or rep filter,
   do not pretend its results are rep-scoped; find an authorized rep-filterable source or
   disclose the limitation.
4. Run independent reads in parallel. Keep access-gated enhancements optional: a
   permission error on an enhancement removes that enhancement, not the whole artifact.

## 3. Stay read-only unless the skill says otherwise

- Never pass `refresh: true` or any equivalent cache-busting argument unless the skill
  explicitly requires it.
- Never call a write, send, note-creation, outcome-recording, or approval-gated
  capability unless the skill explicitly supports it **and** the user has asked for that
  specific write in this conversation **and** any approval flow has completed.
- A diagnostic skill that recommends an action hands off to the write-capable skill or
  product surface. It does not perform the action.

## 4. Exclude fixture and demo records

Inspect provenance, source-channel, generator, and free-text markers before counting any
record. Treat any of the following as test data:

- `synthetic`, `demo_seed`, `demo_fixture`, `seeded`, `fixture`, or generator metadata;
- names or IDs prefixed `[DEMO]` or `demo-`;
- equivalent markers the tenant documents.

Exclude those rows from counts, rates, comparators, timelines, and evidence-depth gates.

When provenance cannot reliably separate fixtures from real records — typically on a
staging or demo tenant — the workflow may still run, but the **entire artifact** must carry
the exact label for its use:

| Artifact use | Required label |
|---|---|
| Commercial, forecast, board, or customer-facing | **Demo data — not for customer or commercial decisions** |
| Employment, performance, or HR | **Demo data — not for employment decisions** |
| Routine coaching | **Demo data — not for real coaching** |

Never let a realistic-looking fixture satisfy a stop gate or a minimum-evidence threshold.

## 5. Missing evidence is unavailable, never zero

- An unavailable tool, an access-denied field, a `null`, or an omitted row is
  **unavailable**. Render it as "unavailable" with the reason, never as `0`, `—`, "none",
  "no risk", or a green status.
- An empty list is only "zero" when the tool's contract says so (for example a verified
  `0` with `_evidence.verified: true`). Otherwise an empty result is **indeterminate**.
- Absence of CRM records is not evidence of absence in the world: no pipeline is not
  proof of whitespace, and no logged activity is not proof of disengagement.
- Never expose raw permission errors, stack traces, or access-denied detail in an
  audience-facing artifact. Summarise the gap in the sources and limits section.

## 6. Correlational language

Signal movement, health movement, interventions, coaching, and framework scores are
**correlational** unless a source proves causation. Do not write "caused", "drove",
"because of", "proved", "predicts", or "will" about these relationships. Prefer "moved
alongside", "coincided with", "is associated with", and state the sample size.

Keep tool-provided scores separate from model-derived judgments, and label which is which.

## 7. Delivery

- Return one clickable link to the final artifact (or the artifact inline when the skill
  delivers in chat), followed by a short note on material evidence gaps and anything
  excluded.
- For slide artifacts, render every slide to an image and inspect it at full size before
  delivery. Fix clipping, overlap, wrapping, placeholder text, chart errors, and any
  number that does not match the source payload.
- No bracketed TODOs, placeholder values, or lorem text in a delivered artifact.

## Preflight checklist

Before the first data read:

- [ ] Connector resolved by logical tool name; deferred tools loaded in one batch
- [ ] `current_context` passed; `scoped_org_id` stored
- [ ] Multiple connectors disambiguated, or only one present
- [ ] Live schemas inspected for every tool the skill will call
- [ ] Write capabilities excluded unless the skill and the user both require them

Before delivery:

- [ ] Returned IDs match `scoped_org_id`
- [ ] Fixture rows excluded, or the whole artifact carries the correct demo label
- [ ] Every missing value rendered as unavailable, with a reason
- [ ] No causal language about correlational evidence
- [ ] Slides rendered and inspected; one link returned
