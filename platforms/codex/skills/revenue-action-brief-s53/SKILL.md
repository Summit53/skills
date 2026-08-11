---
name: revenue-action-brief-s53
description: Generate a prioritized, read-only revenue action brief for a VP Sales or CRO, organized into today, this week, this month, and this quarter. Use live Summit53 CRM evidence to answer what needs attention, what to focus on, where to spend time, or what the leader should do next. Keep this customer-facing and separate from Summit53's internal GTM workflows.
---

# Revenue Action Brief

Turn live customer CRM evidence into a short, prioritized action brief. Keep diagnosis read-only and make any handoff to a write-capable workflow explicit.

## Load the contract

1. Read [references/workflow-spec.md](references/workflow-spec.md) completely before calling tools.
2. Read [references/signal-catalog.md](references/signal-catalog.md) completely before detecting or ranking signals.
3. Read [references/async-envelopes.md](references/async-envelopes.md) completely and use it for `unified_forecast_summary`.
4. Resolve every `references/...` path from this skill's root and treat tool names as semantic capabilities rather than fixed namespaces.

## Resolve live tools

- Use the connected Summit53 connector for the intended tenant. Discover exact schemas before calls.
- Preflight all eight read capabilities named in the workflow, including `unified_forecast_summary` and `get_job`.
- If a source is unavailable, preserve the missing-source note and suppress only signals that depend on it. Do not substitute zero or describe silence as health.
- Do not read Summit53's internal strategy, outreach, or accountability skills. This skill serves customers using their own CRM data.

## Produce and hand off

- Follow the workflow's deterministic signal thresholds, action horizons, evidence citations, confidence treatment, and sparse-data rules.
- Keep the brief itself read-only. Before handing an action to a skill that drafts messages or writes CRM records, obtain the user's explicit request or approval for that next action.
- Return the brief in chat and optionally save a workspace copy with a clickable absolute path.
