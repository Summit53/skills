# Summit53 External Skills

Public, customer-facing Summit53 Revenue Engine skills for Claude and OpenAI Codex.
Claude and Codex packages are maintained separately so each platform receives native
instructions and metadata. Shared evidence-handling contracts live outside both discovered
skill directories and are vendored into self-contained packages.

## Repository layout

```text
platforms/claude/skills/  Claude packages
platforms/codex/skills/   Codex packages, including agents/openai.yaml
shared/canonical/         Shared preflight, evidence and asynchronous-lifecycle contracts
manifests/                Deterministic package fingerprints
tools/                    Validation, synchronization and fingerprint tools
```

This public repository intentionally excludes Summit53's internal GTM skills, personal
workflows, historical baselines, local installation state, customer data and migration
provenance.

## Available packages

| Skill | Claude | Codex | Primary use |
|---|:---:|:---:|---|
| `ae-deal-inspection-prep` | ✓ | ✓ | AE preparation for an internal single-deal inspection |
| `board-revenue-pack` | ✓ | ✓ | Board and investor revenue reporting |
| `competitor-response-card` | ✓ | ✓ | Active-deal competitive response guidance |
| `cs-renewal-forecast` | ✓ | ✓ | Customer Success renewal-book outlook |
| `customer-qbr` | ✓ | ✓ | Customer-facing value and success review |
| `deal-review-prep` | ✓ | ✓ | Manager-led formal deal review |
| `deal-timeline-defence` | ✓ | ✓ | Evidence-grounded opportunity chronology |
| `first-meeting-deck` | ✓ | ✓ | Customer-facing first-meeting presentation |
| `forecast-delta-brief` | ✓ | ✓ | Weekly forecast movement and attribution |
| `qbr-generator` | ✓ | ✓ | Internal quarterly revenue review |
| `renewal-defence-pack` | ✓ | ✓ | Account-level renewal defence |
| `rep-coaching-report` | ✓ | ✓ | Routine developmental coaching and 1:1 preparation |
| `rep-evidence-dossier` | ✓ | ✓ | Neutral evidence dossier for formal rep decisions |
| `revenue-action-brief-s53` | ✓ | ✓ | Prioritized revenue-leader action brief |
| `territory-review` | ✓ | ✓ | Strategic territory review |
| `win-loss-analysis` | ✓ | ✓ | Closed-deal outcome analysis |

## Requirements

- A connected Summit53 Revenue Engine connector with access to the user's authorized tenant.
- The read capabilities required by the selected skill.
- PowerPoint authoring support for skills whose primary artifact is PPTX.

Packages discover Summit53 capabilities by logical name and inspect live schemas before use.
They must verify tenant scope through `current_context` where available and must not hard-code
server namespaces, generated capability hashes or organization IDs. Claude packages vendor
`shared/canonical/connector-preflight.md`, which defines this preflight once.

## Install

Clone the repository, then copy only the desired package directory into the platform's
configured skills directory.

For Codex, copy from:

```text
platforms/codex/skills/<skill-name>
```

For Claude, copy from:

```text
platforms/claude/skills/<skill-name>
```

Restart or begin a new task after installation so the platform refreshes skill discovery.

## Safety model

- Treat every package as tenant-scoped and least-privilege.
- Inspect live capability metadata before calling tools.
- Do not execute writes or approval-gated capabilities unless a skill explicitly supports
  them and the user has made an explicit request and completed the approval flow.
- Exclude fixture, synthetic, seeded and demo records from real commercial or employment
  decisions.
- Label demo or test outputs when provenance cannot distinguish fixture data reliably.
- Preserve missing evidence as unavailable; never substitute zero or invent causality.

## Validate changes

From the repository root:

```powershell
python tools\sync_canonical_references.py --check
python tools\validate_codex_packages.py
python tools\validate_claude_packages.py
python tools\validate_public_boundary.py
python tools\generate_package_fingerprints.py
python tools\generate_package_fingerprints.py --check
```

Run Codex's official `quick_validate.py` against every changed Codex package before release.
When a shared canonical reference changes, run `sync_canonical_references.py --write`, review
the materialized changes in both platform trees, then rerun all validation. To make a package
consume a canonical file, copy it into that package's `references/` folder once; the sync tool
discovers consumers by presence.

Both platform trees must contain the same package names; `validate_public_boundary.py`
enforces this.

## Contributing

Keep Claude and Codex `SKILL.md` files separate. Do not introduce platform conditionals into
one package, do not edit installed copies as source, and do not add internal or customer data
to this repository.
