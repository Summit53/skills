# Summit53

Evidence-grounded revenue workflows for Claude and Codex, built on your own Summit53 Revenue
Engine data. Ask in plain language, such as "why did the forecast move this week?" or "prep a
deal review for Acme", and the matching skill reads your Summit53 tenant and produces a finished
brief, card or slide deck. Every number is scoped to your organisation, and missing evidence is
reported as unavailable, never as zero.

## What's included

- **The Summit53 connector**, the hosted Summit53 MCP server at `https://api.summit53.io/mcp`.
- **17 skills.** Start with `summit53`, which checks your connection, tells you which
  organisation you are connected to, and routes your request to the right workflow:

| Skill | What you get |
|---|---|
| `summit53` | Connection check, setup help and routing to the right workflow |
| `forecast-delta-brief` | One-slide brief explaining this week's forecast movement |
| `board-revenue-pack` | Board-ready revenue deck: what changed since last quarter and why |
| `qbr-generator` | Internal quarterly revenue and sales operating review deck |
| `customer-qbr` | Customer-safe value and success review |
| `revenue-action-brief-s53` | Prioritised actions for a VP Sales or CRO |
| `deal-review-prep` | Manager-led deal review deck with framework scorecards |
| `ae-deal-inspection-prep` | One-page evidence sheet for an account executive's deal inspection |
| `deal-timeline-defence` | Evidence-graded chronology for a disputed deal timeline |
| `competitor-response-card` | One-screen response card for a competitor in an active deal |
| `first-meeting-deck` | Customer-facing first-meeting or discovery deck |
| `win-loss-analysis` | Win/loss patterns across closed deals |
| `cs-renewal-forecast` | Renewal-book outlook for a Customer Success leader |
| `renewal-defence-pack` | Evidence-grounded defence for one account's renewal |
| `rep-coaching-report` | Coaching deck for a routine 1:1 with a sales rep |
| `rep-evidence-dossier` | Neutral evidence dossier for promotion, calibration or HR decisions |
| `territory-review` | Territory and regional performance review deck |

## Requirements

- A Summit53 account that is an approved member of an active Summit53 organisation.
- For slide decks: Claude's `pptx` skill, or Codex's Presentations skill.

## Install

In Claude Code:

```text
/plugin install summit53 --marketplace Summit53/skills
```

In claude.ai, Claude Desktop or Cowork, add the marketplace `https://github.com/Summit53/skills`
under **Customize › Plugins › Add** and install **Summit53**. In Codex:

```bash
codex plugin marketplace add Summit53/skills
codex plugin add summit53@summit53
```

## Connect

After installing, sign in to the Summit53 connector with your Summit53 account (OAuth). No API key
is needed. In Claude Code, run `/mcp`, select **summit53** and choose **Authenticate**. In
claude.ai, Claude Desktop or Cowork, connect Summit53 on the plugin's **Connectors** tab. Then ask:
"Which Summit53 organisation am I connected to?"

Setup guide for every client: https://www.summit53.com/docs/mcp-setup-guide

## What this plugin connects to, sends and writes

- **Summit53 API.** Skills call the Summit53 MCP server at `api.summit53.io` with your signed-in
  account. Requests carry only what a skill needs, such as an opportunity, account or rep
  identifier and a reporting window. Summit53 returns data your Summit53 role is already allowed
  to see. The connector sends data to `api.summit53.io` only.
- **Mostly reads; a few tools save data.** No skill changes your CRM records. Three connector
  tools save data in Summit53 as a side effect, and Claude asks before running them:
  `first-meeting-deck` queues `external_account_research`, which runs public web and news
  research on Summit53's servers and stores the results on the account; `qbr-generator` and
  `revenue-action-brief-s53` call `weekly_action_plan`, which generates and saves your weekly
  plan if one doesn't exist yet; and skills may call `cancel_job` to stop a background job they
  started. Any other write, such as saving coaching notes in `rep-coaching-report`, happens only
  when you ask for that specific change, the connector exposes it and you approve it.
- **Web search.** `first-meeting-deck` runs a small number of public web searches about the
  prospect and its market, using the assistant's own web search tool. `competitor-response-card`
  searches the web only when you ask it to.
- **Local files.** Deck and document skills create PPTX, DOCX or Markdown files in your working
  folder or the assistant's output area. `first-meeting-deck` updates its own vendor-context
  reference files only after you approve the change.
- **No hooks, commands or background processes.** The plugin contains skills, the connector
  reference and a logo, and nothing else runs on your machine.

## Data handling

Skills exclude demo and test records from real decisions and label any output built on data
that cannot be separated from demo records. They describe signals as correlations, not causes,
and never render missing data as zero or a healthy status. Your data is governed by Summit53's
terms: https://summit53.io/terms-of-service

## Support

- Documentation: https://www.summit53.com/docs
- Email: support@summit53.io
- Source and issues: https://github.com/Summit53/skills

## License

Proprietary. See [LICENSE](LICENSE).
