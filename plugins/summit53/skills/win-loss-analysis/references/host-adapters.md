# Host Adapters — Canonical Contract

**Canonical file. Version 1.0.0 · 2026-10-14.**

Maintained once and copied byte-identical into every consuming skill. Bump the version on
edit and re-copy with `tools/sync_canonical_references.py --write`. If two copies
disagree, the higher version wins.

Consumers: every Summit53 skill package.

## Contents

- [Why this exists](#why-this-exists)
- [Identify the host](#identify-the-host)
- [Loading the Summit53 tools](#loading-the-summit53-tools)
- [Building slides](#building-slides)
- [Building documents](#building-documents)
- [Rendering and inspecting slides](#rendering-and-inspecting-slides)
- [Saving and delivering files](#saving-and-delivering-files)
- [Referring to other Summit53 skills](#referring-to-other-summit53-skills)
- [Dates](#dates)

## Why this exists

The same skill packages run in Claude (Claude Code, claude.ai, Claude Desktop, Cowork) and
in OpenAI Codex. The evidence rules, gates and artifact designs are identical on every
host. Only the plumbing differs: how tools load, which presentation toolchain builds a
deck, how a slide is rendered for inspection, and how a file reaches the user. Skills
describe *what* to build host-neutrally and point here for *how* on the current host.

When a skill gives a toolchain-specific instruction (for example a PptxGenJS option), it
applies only on the host that uses that toolchain. Translate the intent, not the API call,
on any other host.

## Identify the host

Use what the session exposes; do not ask the user.

| Signal | Host |
|---|---|
| A `pptx` / `docx` skill is listed, or tools are deferred behind ToolSearch | Claude |
| A `Presentations` / `Documents` skill is listed, or `@oai/artifact-tool` is available | Codex |
| Neither | Generic fallback (below) |

## Loading the Summit53 tools

| Host | How |
|---|---|
| Claude Code | Summit53 tools are usually deferred. Load every tool the skill needs with **one** ToolSearch call whose query is a `select:` list of the full tool names, instead of loading tools one at a time. |
| claude.ai, Desktop, Cowork | Connector tools are available directly once the Summit53 connector is connected. |
| Codex | MCP tools from the `summit53` server are available directly once `codex mcp login summit53` has succeeded. |

On every host the tool prefix differs per installation. Resolve tools by logical name, as
`connector-preflight.md` requires.

## Building slides

The design in each skill (16:9 wide canvas, palette, typography, slide order, chart
choices, label text) is the specification on every host.

| Host | Toolchain |
|---|---|
| Claude | Read the `pptx` skill's SKILL.md and its PptxGenJS reference before writing code, then build with **PptxGenJS** in one Node.js script. Use `pptx.layout = "LAYOUT_WIDE"` (13.33″ × 7.5″) for a 16:9 deck, never `"LAYOUT_16x9"` (10″ × 5.625″), which clips anything placed for a 13.33″ canvas. Create a fresh options object for every `addShape` / `addText` call (factory functions), because PptxGenJS mutates option objects. |
| Codex | Load and follow the **Presentations** skill completely: `@oai/artifact-tool` in JavaScript ES modules, its implementation reference, and its own validation and finalization flow. Do not fall back to `python-pptx`. Map each skill's inch-based layout onto the canvas proportionally. |
| Generic | PptxGenJS in Node.js with the same settings as the Claude row. |

Prefer native, editable charts over images on every host.

## Building documents

| Host | Toolchain |
|---|---|
| Claude | The `docx` skill. |
| Codex | The **Documents** skill. |
| Generic | Any DOCX library; keep native headings and tables. |

Create a DOCX only when the skill or the user asks for one.

## Rendering and inspecting slides

Every skill requires each slide to be rendered to an image and inspected at full size
before delivery. Fix the generator, not the rendered output, then re-render the affected
slides.

| Host | Validate | Render |
|---|---|---|
| Claude | The `pptx` skill's `scripts/office/validate.py` | The `pptx` skill's `scripts/office/soffice.py` → PDF → `pdftoppm` (or `soffice --headless --convert-to pdf`, then `pdftoppm -jpeg -r 150`) |
| Codex | The Presentations skill's finalization checks | The Presentations skill's render step |
| Generic | Open the file with a PPTX library and confirm it parses | `soffice --headless --convert-to pdf`, then `pdftoppm` |

Render caveats:

- **LibreOffice substitutes fonts** such as Georgia and Inter with different metrics, so
  a preview can wrap where PowerPoint would not, or the reverse. Leave about 10% width
  slack in header and title boxes rather than trusting a tight preview fit.
- **No LibreOffice on macOS:** `qlmanage -p -o <dir> deck.pptx` writes `Preview.html`,
  which a browser can show slide by slide (serve the folder on localhost if the browser
  will not open local files). Quick Look does not draw native charts or some shapes, so
  say which elements could not be checked visually rather than claiming a full render.
- **No render path at all:** deliver, and state plainly that the slides were not visually
  inspected.

## Saving and delivering files

| Host | Where to save | How to deliver |
|---|---|---|
| Claude Code, Codex CLI | The working directory, or an `output/` folder in it when one exists | One clickable path or link to the final file |
| claude.ai, Desktop, Cowork | The session's outputs directory | The file card or link the host provides |
| Codex app with an Artifact Session | Follow the Presentations skill's live-artifact delivery | The artifact reference that skill returns |

Deliver one final file per requested artifact. Do not deliver scratch scripts, renders or
intermediate drafts unless asked.

## Referring to other Summit53 skills

Name a sibling skill by its plain name in prose, for example `board-revenue-pack`. Never
write host invocation syntax such as `$board-revenue-pack` or `/summit53:board-revenue-pack`
in a skill body; each host resolves the plain name. A user may invoke a skill with their
host's syntax; treat that as a request for the named skill.

## Dates

Never compare against the host or session clock for evidence dates. It can sit in a
different timezone from the tenant. Use the organization-scoped `as_of` (or the equivalent
date) that the Summit53 tool returns. Use the host date only for labels the user asked for,
such as a file name's run date.
