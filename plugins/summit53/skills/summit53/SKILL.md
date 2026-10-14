---
name: "summit53"
description: "Start here for any Summit53 Revenue Engine request when the right workflow is unclear, and to set up or check the Summit53 connection. Confirms the Summit53 connector is attached and signed in, reports which organization it is scoped to, and routes to the matching Summit53 skill: forecast movement, board pack, internal QBR, customer QBR, deal review, deal inspection, deal chronology, competitor response, first-meeting deck, renewal outlook, renewal defence, rep coaching, rep evidence dossier, territory review, win/loss analysis or the revenue action brief. Use on 'set up Summit53', 'connect Summit53', 'is Summit53 connected', 'which Summit53 org am I in', 'what can Summit53 do', 'which Summit53 skill should I use', or a revenue question that names Summit53 without naming a workflow."
metadata:
  version: "1.1.0"
  baselined: "2026-10-14"
  status: "active"
---

# Summit53 (start here)

The entry point for the Summit53 skills. This skill checks the connection, then hands off.
It produces no artifact of its own.

## 1. Check the connection

Follow sections 1 and 2 of
[references/connector-preflight.md](references/connector-preflight.md): find the Summit53
tools by logical name and call `current_context`.

- **It succeeds.** Tell the user, in one line, the organization name, their user, and that
  the connection is live. If `organization.is_demo` is `true`, add that this is a Summit53
  demo tenant with synthetic data, so every artifact will carry a demo label (see
  [Demo tenants](references/connector-preflight.md#demo-tenants)). Then route (section 2). If the user only asked to check or set
  up the connection, stop here and offer three example requests from the routing table.
- **No Summit53 tools are present.** Help the user connect (section 3). Do not attempt
  the workflow on general knowledge.
- **The call fails with an authentication or authorization error.** The user must sign in
  again (section 3). If they are signed in but `current_context` reports an inactive user
  or an unapproved membership, a Summit53 admin must approve their membership. Say so
  plainly; do not retry in a loop.
- **More than one Summit53 connector answers.** Installing this plugin alongside a
  manually added connector gives two connectors for the same organization. That is
  harmless: use either one and never merge results across them. If they resolve to
  *different* organizations, ask which one the user means.

## 2. Route

Read the matching skill's `SKILL.md` next and follow it. Each skill runs its own full
preflight, so do not repeat any data reads here.

| The user wants | Skill |
|---|---|
| Why the forecast number moved this week; commit-call prep | `forecast-delta-brief` |
| Board or investor revenue pack; "market or execution?" | `board-revenue-pack` |
| Internal quarterly operating review | `qbr-generator` |
| Customer-facing QBR, EBR or value review | `customer-qbr` |
| Prioritized actions for a VP Sales or CRO (today / week / month / quarter) | `revenue-action-brief-s53` |
| Manager-led formal review of one deal (deck) | `deal-review-prep` |
| An AE preparing to be inspected on one deal (one-page sheet) | `ae-deal-inspection-prep` |
| A disputed chronology: "when did it go dark?", close-date or handoff challenge | `deal-timeline-defence` |
| A competitor just appeared in an active deal; competitive talk track | `competitor-response-card` |
| Historical or portfolio-level win/loss patterns | `win-loss-analysis` |
| First-meeting or discovery deck for one account | `first-meeting-deck` |
| Renewal-book outlook for a CS leader | `cs-renewal-forecast` |
| Defending one account's renewal; save plan | `renewal-defence-pack` |
| Routine developmental 1:1 coaching deck for a rep | `rep-coaching-report` |
| Promotion case, PIP, calibration or HR evidence | `rep-evidence-dossier` |
| Territory, regional or whitespace review | `territory-review` |

When two rows fit, ask one short question that names both options. If nothing fits, say
what the skills cover and answer from the connector's tools directly, following the
preflight contract.

## 3. Connect Summit53

The connector is the hosted Summit53 MCP server at `https://api.summit53.io/mcp`. It signs
users in with their own Summit53 account (OAuth), so no API key is needed. Give only the
steps for the user's host.

**Claude Code, with this plugin installed:** the plugin already registers the server. Run
`/mcp`, select **summit53**, choose **Authenticate**, and complete the browser sign-in.

**Claude Code, skills installed without the plugin:**

```bash
claude mcp add --transport http summit53 https://api.summit53.io/mcp
```

Then authenticate through `/mcp` as above.

**claude.ai, Claude Desktop or Cowork:** open the Summit53 plugin's **Connectors** tab and
connect **Summit53**, or, without the plugin, add a custom connector with the URL above
under **Settings › Connectors**. Then sign in. On a Team or Enterprise plan an
Owner may first need to add the connector under **Organization settings › Connectors**.

**Codex:**

```bash
codex mcp add summit53 --url https://api.summit53.io/mcp
codex mcp login summit53
```

After connecting, start a new conversation or task so the tools load, then ask again.
