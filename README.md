# Summit53 External Skills

Public, customer-facing Summit53 Revenue Engine skills for Claude and OpenAI Codex, shipped as
one plugin that also bundles the hosted Summit53 MCP connector. Install it once, sign in with
your Summit53 account, and ask.

## Repository layout

```text
.claude-plugin/marketplace.json  Claude plugin marketplace
.agents/plugins/marketplace.json Codex plugin marketplace
plugins/summit53/                The summit53 plugin (one copy, both hosts)
  .claude-plugin/plugin.json     Claude plugin manifest
  .codex-plugin/plugin.json      Codex plugin manifest
  .mcp.json                      Bundled hosted Summit53 MCP connector
  skills/<name>/SKILL.md         One package per skill, including the `summit53` router
  skills/<name>/agents/          Codex UI metadata (openai.yaml); ignored by Claude
  skills/<name>/references/      Vendored canonical contracts plus skill-specific references
shared/canonical/                Shared preflight, evidence and asynchronous-lifecycle contracts
manifests/                       Deterministic package fingerprints
tools/                           Validation, synchronization and fingerprint tools
```

This public repository intentionally excludes Summit53's internal GTM skills, personal
workflows, historical baselines, local installation state, customer data and migration
provenance.

## Available packages

Every skill runs on Claude Code, claude.ai, Claude Desktop, Cowork and Codex.

| Skill | Primary use |
|---|---|
| `summit53` | Start here: connection check, setup help and routing |
| `ae-deal-inspection-prep` | AE preparation for an internal single-deal inspection |
| `board-revenue-pack` | Board and investor revenue reporting |
| `competitor-response-card` | Active-deal competitive response guidance |
| `cs-renewal-forecast` | Customer Success renewal-book outlook |
| `customer-qbr` | Customer-facing value and success review |
| `deal-review-prep` | Manager-led formal deal review |
| `deal-timeline-defence` | Evidence-grounded opportunity chronology |
| `first-meeting-deck` | Customer-facing first-meeting presentation |
| `forecast-delta-brief` | Weekly forecast movement and attribution |
| `qbr-generator` | Internal quarterly revenue review |
| `renewal-defence-pack` | Account-level renewal defence |
| `rep-coaching-report` | Routine developmental coaching and 1:1 preparation |
| `rep-evidence-dossier` | Neutral evidence dossier for formal rep decisions |
| `revenue-action-brief-s53` | Prioritized revenue-leader action brief |
| `territory-review` | Strategic territory review |
| `win-loss-analysis` | Closed-deal outcome analysis |

## Requirements

- A connected Summit53 Revenue Engine connector with access to the user's authorized tenant.
- The read capabilities required by the selected skill.
- PowerPoint authoring support for skills whose primary artifact is PPTX.

Packages discover Summit53 capabilities by logical name and inspect live schemas before use.
They must verify tenant scope through `current_context` where available and must not hard-code
server namespaces, generated capability hashes or organization IDs. Every package vendors
`shared/canonical/connector-preflight.md`, which defines this preflight once, and
`shared/canonical/host-adapters.md`, which holds the only host-specific instructions (tool
loading, slide and document toolchains, rendering, delivery).

## Install

### Claude Code

```text
/plugin marketplace add j-sulliman/summit53-external-skills
/plugin install summit53@summit53
/reload-plugins
```

The plugin bundles the hosted Summit53 MCP connector. Run `/mcp`, select **summit53**, choose
**Authenticate** and sign in with your Summit53 account. To verify, ask
*"Which Summit53 organization am I connected to?"*

Update with `/plugin marketplace update summit53`; turn on auto-update for the marketplace in
`/plugin` so new versions arrive without asking. Uninstall with `/plugin uninstall summit53@summit53`.

### claude.ai, Claude Desktop and Cowork

Add this repository as a marketplace under **Customize › Plugins › Add**, install **summit53**,
then connect **Summit53** on the plugin's **Connectors** tab. Plugins installed here also sync
into Claude Code.

Team and Enterprise Owners can roll it out to everyone from **Organization settings › Plugins &
skills** (set the plugin to **Installed by default** or **Required**) and must also add the
Summit53 connector under **Organization settings › Connectors**; each member then signs in
with their own account.

### Codex

```bash
codex plugin marketplace add j-sulliman/summit53-external-skills
codex plugin add summit53@summit53
```

Or open `/plugins` in Codex, choose the **Summit53** marketplace and install. Codex asks you to
sign in to the bundled connector at install time. If the Summit53 tools do not appear, add the
connector directly:

```bash
codex mcp add summit53 --url https://api.summit53.io/mcp
codex mcp login summit53
```

Update with `codex plugin marketplace upgrade summit53`. Begin a new task after installing so
skills and tools load.

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

```bash
python3 tools/sync_canonical_references.py --check
python3 tools/validate_packages.py
python3 tools/validate_public_boundary.py
python3 tools/validate_plugin_manifests.py
claude plugin validate .
claude plugin validate plugins/summit53
python3 tools/generate_package_fingerprints.py --check
```

Before release, also run Codex's official checks (they need PyYAML):

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/summit53/skills/<name>
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/summit53
```

When a shared canonical reference changes, run `sync_canonical_references.py --write`, review
the materialized changes, then rerun all validation. To make a package consume a canonical
file, copy it into that package's `references/` folder once; the sync tool discovers consumers
by presence. After any package change, run `generate_package_fingerprints.py` to refresh the
manifest.

## Releasing

Bump `version` in **both** `plugins/summit53/.claude-plugin/plugin.json` and
`plugins/summit53/.codex-plugin/plugin.json` on every release. `validate_plugin_manifests.py`
fails if they disagree. Claude Code and Codex only deliver an update when the version changes.

## Contributing

- One `SKILL.md` per skill serves every host. Write evidence rules, gates and artifact designs
  host-neutrally. Put host mechanics (tool loading, the `pptx`/Presentations toolchains,
  rendering, file delivery) in `shared/canonical/host-adapters.md`, and link to it from the
  skill. When a toolchain-specific detail must stay in a skill, frame it as
  "When building with PptxGenJS (Claude's pptx skill), …".
- Frontmatter is `name`, `description` and `metadata: {version, baselined, status}` only.
  Codex rejects other top-level keys.
- Refer to sibling skills by plain name, never as `$name` or `/summit53:name`.
- Do not edit installed copies as source, and do not add internal or customer data to this
  repository.
