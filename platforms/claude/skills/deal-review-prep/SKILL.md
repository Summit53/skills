---
name: "deal-review-prep"
description: "Build a manager-led, evidence-based deal review PPTX for one Summit53 opportunity: health verdict, first constraint, MEDDPIC/BANT/SPICED scorecards, risk factors, blockers, account and stakeholder context, coaching questions and next steps. Use when a sales manager or revenue leader wants to prep for a deal review or pipeline review meeting, review a specific deal, do a deal deep-dive, build a deal scorecard or assess deal health, e.g. 'review this deal', 'deal review for opportunity [ID]', 'how healthy is the [deal] deal', 'what's the risk on [deal]', 'is this deal going to close', 'should I be worried about [deal]', 'give me the full picture on [deal]'. Do not use for an AE's own inspection prep — use ae-deal-inspection-prep. Do not use for a contested deal chronology — use deal-timeline-defence. For a competitor response in an active deal use competitor-response-card; for drafting outreach or re-engagement use deal-action-engine (if installed)."
version: "1.2.0"
baselined: "2026-10-13"
status: "active"
---

# Deal Review Prep

Generate a structured, coaching-ready deal review deck for one opportunity by pulling live data from Summit53 and assembling it into a polished PPTX. This is the "everything you need in 30 seconds" prep for a manager-led pipeline review or 1:1 coaching conversation. Keep facts, model inferences and recommended actions visibly distinct.

## Route first

- Use this skill only for a manager-led formal review, or a PPTX artifact, about **one** deal.
- The owning AE preparing for their own inspection (likely questions, answer practice, a cheat sheet) → `ae-deal-inspection-prep`.
- A challenged or contested chronology, inactivity onset, or evidence trail → `deal-timeline-defence`.
- A one-screen response to a named competitor in an active deal → `competitor-response-card`. This skill only adds a short battlecard callout.
- Drafting, sending or executing emails, notes or rescue actions → `deal-action-engine` when installed. Never execute them here.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its checklist before any data call. It covers tenant resolution (`current_context` first), picking between multiple Summit53 connectors, loading deferred tools in one ToolSearch `select:` batch, live-schema discovery, read-only discipline, fixture exclusion, unavailable-is-not-zero, correlational language and one-link delivery.

Skill-specific gates:

1. **Resolve exactly one opportunity before any other read.** Use the supplied opportunity ID when given. A deal or account name that matches more than one opportunity is ambiguous: list the candidates (name, account, amount, stage, close date, owner) and ask the user to pick. Never pick silently, and never merge two deals.
2. **Confirm scope.** The opportunity's organization (and the account's, where returned) must match `scoped_org_id`. On mismatch, stop and report both IDs.
3. **Check optional capabilities.** Use `list_available_tools` to confirm whether `get_opportunity_signals`, `prepare_dark_deal_rescue`, `opportunity_stakeholder_intelligence`, `get_battlecard` and the target-account tools (`search_target_accounts`, `get_target_account`; Outreach plan) are exposed on this connector. Missing or access-gated enhancements remove their section, never the deck.
4. **Demo label.** This is a commercial artifact. If fixture rows cannot be separated from real records, put **Demo data — not for customer or commercial decisions** on the title slide and in the footer of every slide.

## Why This Exists

Before every pipeline review, managers scramble to pull deal data, cross-reference qualification frameworks, and figure out the right questions to ask. AEs scramble to make sure they have answers. This skill does it in one shot: live CRM data flows into a professional deal review deck with specific risk factors, framework gaps, and suggested coaching questions. It turns a deal number into a coaching conversation.

## Step 1: Identify the Deal

You need an opportunity ID. If the user provides one, call `get_opportunity` directly with it — this is the fastest and most complete path, returning health score, final amount, contract term, and discount fields that `search_opportunities` doesn't expose.

If they give you a deal name or account name instead:

1. Call `search_opportunities` with the deal or account name as the query
2. If multiple results come back, show them and ask the user to pick one. Do not continue until the deal is unambiguous — a near-match name is not a match
3. Once you have the opportunity ID, call `get_opportunity` to get the full deal record
4. Note the account ID from the result (you'll need it for account context)

If the user says something like "review my biggest deal" or "look at the riskiest deal", use `risk_heatmap` or `search_opportunities` sorted appropriately to find it, confirm with the user, then call `get_opportunity` to fetch full details. "Riskiest" means the lowest `healthScore` / `Low` `healthBand` — never sort by the deprecated `riskScore` alias as if higher meant riskier.

## Step 2: Pull All Data

Launch these calls in parallel where possible — they're mostly independent. You need the opportunity ID and account ID from Step 1. Argument names below are semantic guidance: inspect each tool's live schema first and follow it where it differs (see the preflight). Never pass `refresh: true`.

### Required Data Pulls

1. **Deal Details & Risk**
   - `get_opportunity` with the opportunity ID — the primary deal record: name, amount, stage, close date, forecast category, rep, health score, final amount, contract term, discount. Use this instead of `search_opportunities` for single-deal lookups.
   - `risk_heatmap` filtered to find this specific deal — `healthScore`, `healthBand`, score freshness, and risk-factor breakdown. Treat `score_semantics` as authoritative: higher health is better and `riskScore` is only a deprecated alias.
   - `deal_drag_dashboard` filtered to this deal (use `min_score: 0` to capture all deals, then find this opportunity by ID) — waste score, staleness %, activity level, drag cause, and recovery strategy. A deal can have a moderate risk score but a high waste score if it has been stalled for weeks — this gives the complementary "cost of inaction" view.
   - `get_opportunity_signals` with the opportunity ID — the Revenue Signal Layer: a single ranked "first constraint to fix," win-probability movement, and evidence-scored signals. **Access-guarded** (leader/owning rep only) — attempt the call when the tool is exposed, but if it returns an access-denied error or empty result, degrade gracefully and fall back to the hand-derived verdict from risk + framework scores in Step 3. Never let this block deck generation, and never put the access-denied detail in the deck — the Sources & Limits slide just lists "Signal layer: unavailable".

2. **Deal Narrative** (run in parallel with framework analysis)
   - `get_opportunity_notes_summary` with the opportunity ID — the AI-generated narrative of what has actually happened on this deal: objections raised, commitments made, competitive dynamics, next steps. This is the qualitative backbone of the review.
   - `get_opportunity_notes` with `limit: 5` as a FALLBACK — if `get_opportunity_notes_summary` returns null or empty, pull raw notes as backup for the Narrative slide.
   - `get_opportunity_activities` with the opportunity ID — full activity log (calls, emails, meetings, notes) in chronological order. Reveals cadence, last touch, and whether the deal has gone cold.

3. **Framework Analysis** (run all three in parallel)
   - `opportunity_framework_summary` with `framework: "MEDDPIC"` and the opportunity ID — the primary qualification framework
   - `opportunity_framework_summary` with `framework: "BANT"` and the opportunity ID — budget/authority/need/timeline view
   - `opportunity_framework_summary` with `framework: "SPICED"` and the opportunity ID — situation/pain/impact/critical event/decision

4. **Account Context**
   - `account_execution_health` with the account ID — account-level health score and deal-level breakdown
   - `opportunity_stakeholder_intelligence` with the opportunity ID — buying-committee map, coverage gaps (e.g., missing economic buyer), and suggested engagement moves. Feeds the Stakeholder Coverage subsection on Slide 8 and operationalizes the "single-threaded deal" risk flag from Step 3.
   - `search_opportunities` filtered by account ID — other open deals at this account (for context)
   - **Conditional**: If the account has high ARR (> 500K) or multiple contracts, call `get_value_impact_card` with the account ID to surface fulfilment score and expansion readiness.
   - **Conditional**: For expansion or renewal-motion accounts (multiple contracts, or another open Closed Won/renewal deal at the account), also call `account_health_movement` with the account ID to get the trend direction (improving/declining) alongside the point-in-time score. This is **correlational** — describe it as "trending," never as "caused by" any single deal.

5. **Activity & Engagement**
   - `activity_gaps` with the account's owner ID — last activity date, engagement status for this account

6. **Value Realization** (conditional — only for Closed Won deals)
   - If `get_opportunity` returns stage = "Closed Won", call `get_value_contract` with the opportunity ID to pull promised outcomes, metrics, and expansion signals.

7. **Dark Deal Rescue Packet** (conditional — only if the deal is flagged "going cold" per the Activity Cadence Assessment in Step 3, or receives a Red health verdict)
   - `prepare_dark_deal_rescue` with the opportunity ID — a shadow-mode rescue packet: overdue-close diagnosis, stakeholder gaps, a drafted re-engagement email, and a suggested action plan. This tool is **read-only/shadow-mode evidence only** — it drafts, it does not send or execute anything. Use its diagnosis, stakeholder gaps and action plan as evidence for the review; never present any of it as an action already taken, and never send or execute it from this skill. The drafted email stays out of the deck — if the user wants to work on outreach, hand off to `deal-action-engine` (if installed).
   - **Deployment note**: `prepare_dark_deal_rescue` is not exposed on every deployment (historically staging-only). Check `list_available_tools` before calling; if it's unavailable, skip the call entirely and skip the rescue appendix on Slide 10 — don't error or block deck generation.

8. **Competitive Battlecard** (conditional — only if the notes summary or framework evidence names a specific competitor)
   - `get_battlecard` for the named competitor — differentiation talking points and positioning guidance. Powers the Competitive Positioning callout on Slide 4. Use only an exact match on the competitor named in the evidence; skip entirely if no competitor is named anywhere in the pulled data. A full competitor response belongs in `competitor-response-card`.

9. **Target-Account Committee Coverage** (conditional — only if the opportunity came from a converted outreach target account; optional enhancement that requires the customer's Outreach plan)
   - There is no direct opportunity → target-account lookup. Call `search_target_accounts` with `query` set to the account name. Use a result only when its `opportunity_id` equals this opportunity's ID (or, when `opportunity_id` is absent, its `crm_account` matches this account **and** the user confirms). A name match alone is not a match; several candidates without a matching `opportunity_id` means skip.
   - `get_target_account(target_account_id)` for the confirmed match → `committee[]` (`committee_role`, `engaged`, `last_touch_date`), `coverage.roles[]` (each role `missing`, `mapped` or `engaged`), `coverage.gaps`, `engagement_model` and `converted_at`.
   - Treat it as **Observed** evidence from the pre-opportunity outreach record, dated by each `last_touch_date` and the target account's `converted_at`: which buying roles were mapped, which were engaged, and which required roles are missing (e.g. "Economic buyer: mapped, never engaged — last touch 2026-08-14"). It feeds the Stakeholder Coverage subsection on Slide 8 and corroborates (or contradicts) `opportunity_stakeholder_intelligence`; where the two disagree, show both with their source and date rather than picking one.
   - A `single_threaded` target account has `coverage_applicable: false` and `coverage_pct: null` — committee coverage was not measured by design. Say so; never render it as 0% or as a gap.
   - Read-only. Never call create/update/convert target-account tools or any stakeholder-suggestion write.

### Handling Missing Data

Don't fail if data is sparse — adapt. Missing data is **never zero and never a positive signal**: an unavailable tool, an access-gated field, a `null` or an empty list is "unavailable" (or "indeterminate"), stated with its reason in the Sources & Limits slide. Record every unavailable, empty, stale or contradictory source as you go.
- If `get_opportunity_notes_summary` returns no summary, pull the 3 most recent raw notes from `get_opportunity_notes` as a fallback for the Narrative slide. Render as bullet points and label as "Recent Notes (summary unavailable)" to distinguish from the AI summary.
- If `get_opportunity_activities` returns empty, note "No activities logged on this deal" — that is a CRM-logging fact, not proof the buyer is disengaged
- If a framework summary returns an error or empty data, skip that framework and note "Framework data unavailable"
- If account execution health is empty, note "No account health data available" and move on
- If `activity_gaps` returns nothing for this account, treat it as **indeterminate**, not good — note "Engagement gaps: indeterminate (no rows returned)". Only a verified zero in the tool's own contract counts as "no gaps"
- If `get_value_impact_card` returns no data, skip the Value & Expansion Health subsection on Slide 8
- If `get_value_contract` returns no data for a Closed Won deal, note "No value contract available" on the Value Realization slide
- If `get_opportunity_signals` is inaccessible (access-guarded to leader/owning rep) or returns empty, fall back to the hand-derived Deal Health Verdict from risk + framework scores — don't surface the error in the deck; list "Signal layer: unavailable" on the Sources & Limits slide
- If `prepare_dark_deal_rescue` is unavailable (not deployed on this server) or the deal doesn't meet the cold/Red condition, skip the Dark Deal Rescue appendix on Slide 10 entirely
- If `opportunity_stakeholder_intelligence` returns no data, note "Stakeholder map unavailable" on Slide 8 and skip the coverage-gap callouts
- If `get_battlecard` returns no match for the named competitor, skip the Competitive Positioning callout on Slide 4
- If the target-account tools are unavailable, plan-gated or denied, or no target account matches this opportunity, omit the target-account coverage lines on Slide 8 and list "Target-account committee coverage: unavailable" (or "no converted target account matched") on Sources & Limits. That is not evidence the deal is single-threaded
- If `account_health_movement` returns no trend data, show the point-in-time `account_execution_health` score alone, with no trend arrow
- The deal might be new with limited data — that's fine, the deck will just be lighter

## Step 3: Analyze and Synthesize

Before building slides, synthesize the raw data into actionable coaching insights. This is what makes the deck useful.

**Keep tool scores and model judgments apart.** `healthScore`, `healthBand`, waste score, framework percentages, fulfilment score and win-probability movement are **tool-provided** — show them exactly as returned, with their as-of time. The Deal Health Verdict, blockers, cadence flags, coaching questions and next steps are **model-derived judgments** — label them as the reviewer's assessment, never overwrite or "adjust" a tool score with them, and say which evidence each one rests on. Signal, activity, framework and account-health relationships are correlational: no "caused", "drove", "because of" or "will close" language.

### Deal Health Assessment

Look at the server-supplied `healthBand` and framework scores together to create a one-line deal health verdict:
- **Green (Healthy)**: `healthBand: High` and MEDDPIC average > 70%. "This deal is well-qualified and on track."
- **Yellow (Needs Attention)**: `healthBand: Medium`, or MEDDPIC average 40-69%. "Winnable, but gaps need closing."
- **Red (At Risk)**: `healthBand: Low`, or MEDDPIC average < 40%. "Significant risk — needs intervention this week."

If `healthBand` is absent, derive only from the response's declared `score_semantics`; do not apply inverted thresholds to `riskScore`. If the score is stale, show its age next to the verdict and reduce its evidentiary weight.

Cross-reference the health verdict against the notes summary. If the notes describe competitive threats, pricing pressure, procurement resistance, or stalled next steps, escalate the verdict accordingly even if the quantitative scores look acceptable — and say so ("Assessment escalated to Red on note evidence; tool health band remains Medium"). The tool's band stays as returned.

**If `get_opportunity_signals` data is available**, prefer it: use its ranked "first constraint to fix" as the headline of the Deal Health Verdict instead of a generic risk/framework label, and use the win-probability movement (up/down/flat) as a secondary signal — if it's moving down, escalate the verdict color even if risk and framework scores haven't caught up yet. Cross-reference the signals' evidence scores the same way you cross-reference notes. If `get_opportunity_signals` is unavailable (access-guarded or empty), fall back to the hand-derived risk/framework verdict above — this is the default path, not a failure state.

### Blocker Detection

Scan the framework summaries **and the notes summary** for blockers. A blocker is any framework element that:
- Scores below 30% in MEDDPIC
- Has explicit "blocker" or "risk" language in the evidence
- Is a critical-path element (Champion, Economic Buyer, Paper Process) scoring below 50%
- Is called out in the notes summary as an unresolved issue (e.g., "paper process still unresolved", "no executive sponsor confirmed")
- Is flagged by `get_opportunity_signals` as an evidence-scored blocking signal, or matches its ranked "first constraint to fix"

List each blocker with the evidence from the framework analysis, notes, and/or signals data. If `get_opportunity_signals` returned a "first constraint to fix," lead the blocker list with it — it's the single highest-leverage item to raise in the review.

### Activity Cadence Assessment

From `get_opportunity_activities`, assess the deal's engagement health:
- When was the last activity? If > 14 days ago on a deal closing within 60 days, flag as "Going cold"
- Is there a clear next step visible in recent activities/notes? If not, flag as "No next step defined"
- Are activities spread across multiple contacts, or concentrated on one person? Single-threaded deals are higher risk.

If this assessment flags the deal "Going cold," or the Deal Health Assessment above lands on Red, that's the trigger to pull `prepare_dark_deal_rescue` (Step 2, item 7) and build the Dark Deal Rescue appendix on Slide 10. Cross-check the single-threaded flag against `opportunity_stakeholder_intelligence`'s coverage gaps and, when a converted target account matched, its `coverage.roles[]` — a "concentrated on one person" read from activities, a missing economic buyer from stakeholder intelligence, and an economic buyer that was mapped but never engaged during outreach are the same underlying risk seen three ways.

### Suggested Coaching Questions

For each gap or blocker, generate 1-2 specific questions a manager could ask in the review. These should be:
- Concrete, not generic ("Who is your champion at Acme?" not "Do you have a champion?")
- Forward-looking ("What's your plan to get the CFO's sign-off by March 20?" not "Why haven't you done this?")
- Evidence-seeking ("Walk me through the decision process — who are the three people who need to say yes?")
- Grounded in the notes where possible ("The Feb 1 note says procurement is pushing back on price — what's your counter since then?")

### Recommended Next Steps

Based on the full picture, synthesize 3-5 specific next steps. Each should:
- Reference specific evidence from the data (scores, notes, activities)
- Have a clear action and implied timeline
- Be ordered by impact (most important first)

## Step 4: Build the Deck

Build with PptxGenJS following the `pptx` skill: read its SKILL.md (and its PptxGenJS reference, where the installed version has one) before writing any code. Use the **Midnight Executive** design system for visual consistency with other Summit53 deliverables.

### Design System

| Role | Color | Hex |
|------|-------|-----|
| Primary (dark backgrounds) | Navy | `1E2761` |
| Secondary (light text, accents) | Ice Blue | `CADCFC` |
| Accent (highlights, positive) | Emerald | `10B981` |
| Warning | Amber | `F59E0B` |
| Danger | Red | `EF4444` |
| Text on dark | White | `FFFFFF` |
| Text on light | Charcoal | `1E293B` |
| Light background | Off-white | `F8FAFC` |
| Subtle border/divider | Slate | `64748B` |
| Light Slate (dividers, grid) | Light Slate | `E2E8F0` |

**Typography**: Georgia headers (36-44pt), Calibri body (14-16pt).
**Layout**: 16:9 widescreen. 0.5" margins minimum. Dark title/close slides, light content slides.

### Slide Structure

Build these slides in order. The deck is designed to be a focused, single-deal deep-dive — tight enough for a 5-10 minute pipeline review conversation. For Closed Won deals, the Value Realization slide (Slide 9) provides post-sale context; for open deals, Recommended Next Steps moves to Slide 10. Slide numbering adjusts accordingly.

The structure is the default, not a cage: keep the compact evidence-first narrative, but adapt layouts or slide count when the evidence requires it — split a slide that will not fit legibly, merge or drop a section whose sources were all unavailable (and list it on Sources & Limits instead of rendering an empty frame).

---

#### Slide 1: Title Slide
- **Background**: Navy (`1E2761`)
- **Content**: Deal name as the main title, account name, amount, and close date as subtitle. "Deal Review Prep" label. Date and "Powered by Summit53" at bottom.
- **Layout**: Centered, clean. Large Georgia title, Calibri subtitle.

---

#### Slide 2: Deal Snapshot
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `get_opportunity`, `risk_heatmap`, `deal_drag_dashboard`, `get_opportunity_signals` (when accessible)
- **Layout**: Top row — 6 stat cards showing the key deal facts:
  - Deal Amount (formatted as currency)
  - Stage (current stage name)
  - Close Date (formatted)
  - Health Score and Health Band (color-coded from the server value: `High` emerald, `Medium` amber, `Low` red)
  - Forecast Category
  - Waste Score (color-coded: emerald < 15, amber 15-25, red ≥ 26 — with staleness % shown below as a sub-label)
- **Stat card sizing is critical**: The value text inside each card must be 24pt max (not larger) and the label below each card should be 11-12pt. This keeps text from overflowing or wrapping awkwardly when values are long (e.g., "Negotiation", "Best Case"). Cards should be roughly 1.9" wide × 1.1" tall each with 0.12" gaps, starting at y=1.1". If a value would still wrap at 24pt, shrink to 20pt rather than letting it break across lines.
- Label the stat cards as tool values (small "Source: Summit53" caption with the score's as-of date). If the health score is stale, show its age on the card.
- Below the cards: a one-line "Deal Health Verdict" (labelled "Assessment" — it is a model judgment) from your synthesis in Step 3, using a colored background strip matching the health band (emerald/amber/red). When `get_opportunity_signals` is available, lead the verdict with its ranked "first constraint to fix" and note the win-probability movement (e.g., "First constraint: no economic buyer confirmed — win probability trending down") instead of a generic framework label; otherwise use the hand-derived verdict. If the waste score is high (≥ 26) while `healthBand` is `Medium` or `High`, call this out explicitly: "Deal stalled — high staleness despite a non-low health band."
- Include rep name and deal age if available.

---

#### Slide 3: Deal Narrative & Activity
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `get_opportunity_notes_summary` (with `get_opportunity_notes` as fallback), `get_opportunity_activities`
- **Layout**: Two sections side by side or stacked depending on content volume.
  - **Left/Top — Deal Narrative**: The AI notes summary in a clean text block with an Ice Blue left border accent. Show the key developments, critical new information, and stated next steps from the summary. If no summary is available or returns empty, show the 3 most recent raw notes from `get_opportunity_notes` as bullet points. Label fallback notes as "Recent Notes (summary unavailable)" to distinguish from the AI summary.
  - **Right/Bottom — Recent Activity**: A timeline of the last 5 activities from `get_opportunity_activities`, showing type (📧 email, 📞 call, 🤝 meeting, 📝 note), date, summary, and contact name. Use a vertical timeline layout with a thin line connecting entries. Color the most recent activity entry with an Ice Blue background.
- Include a "Last Activity" callout at the top right — e.g., "Last touch: 16 days ago" — color-coded amber if > 14 days, red if > 30 days, emerald if < 7 days.
- This slide grounds the quantitative scores in what's actually happening on the ground.

---

#### Slide 4: Risk Factors
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `risk_heatmap` (risk factors for this deal), `get_battlecard` (conditional)
- **Layout**: Show each risk factor as a card with a colored left border (red for high severity, amber for medium). Each card has the risk factor name as a bold header, and the detail/description below. Arrange in a grid layout (2 columns) or vertical stack depending on count.
- **Competitive Positioning callout** (conditional — only if a competitor was named in the notes or framework evidence and `get_battlecard` returned data): Add a distinct callout box with the competitor's name, 2-3 concrete differentiation talking points from the battlecard, and any landmines to avoid. Skip this callout entirely if no competitor was named — don't force it.
- If `risk_heatmap` returned this deal with a current score and an explicitly empty factor list, show a neutral (slate, not emerald) callout "No risk factors returned by the risk model" with the score's as-of date. If the deal was missing from `risk_heatmap`, or the call failed, show "Risk factors unavailable" instead — absence of rows is not absence of risk.

---

#### Slide 5: MEDDPIC Scorecard
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `opportunity_framework_summary` (MEDDPIC)
- **Layout**: This is the core coaching slide. Show each MEDDPIC element as a row or card:
  - Element name (Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion, Paper Process)
  - Score as a percentage with color coding (emerald ≥ 70%, amber 40-69%, red < 40%)
  - Key evidence or gap summary (1 line from the framework data)
- Use a horizontal bar or progress-bar visual for each score if possible, or a clean table with colored score cells.
- Highlight the weakest elements with a visual marker (red indicator or bold callout).

---

#### Slide 6: Framework Comparison (BANT & SPICED)
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `opportunity_framework_summary` (BANT and SPICED)
- **Layout**: Two-column layout. Left column: BANT scores (Budget, Authority, Need, Timeline) each with score and one-line evidence. Right column: SPICED scores (Situation, Pain, Impact, Critical Event, Decision) each with score and one-line evidence.
- Color-code scores consistently. This gives managers a second lens beyond MEDDPIC — different frameworks surface different gaps.
- If either framework returned no data, use the full width for whichever one is available.

---

#### Slide 7: Blockers & Red Flags
- **Background**: Off-white (`F8FAFC`)
- **Data source**: Synthesized from Step 3 blocker detection (framework scores + notes summary + `get_opportunity_signals`, when accessible)
- **Layout**: Each blocker gets a card with a red left border accent. Card contains:
  - Blocker name (bold, e.g., "No Identified Champion")
  - Evidence from the framework analysis and/or notes summary (what's missing or what was said)
  - Suggested question for the review (from your synthesis)
- If `get_opportunity_signals` returned a ranked "first constraint to fix," make it the first card on the slide with a distinct visual marker (e.g., a "Top Priority" ribbon) so the highest-leverage blocker is unmistakable.
- This slide directly feeds the coaching conversation — the manager can look at each card and ask the corresponding question.
- If no blockers were found **and** MEDDPIC data was available for every critical-path element, show a callout "No critical blockers identified in the available evidence." If any framework or the notes summary was unavailable, say which, and do not call the deal well-qualified.

---

#### Slide 8: Account Context
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `account_execution_health`, `account_health_movement` (conditional), `search_opportunities` (other deals at this account), `get_value_impact_card` (conditional), `opportunity_stakeholder_intelligence`
- **Layout**: Top section — Account health score as a large stat callout with color coding, with a trend arrow (▲ improving / ▼ declining / ▬ flat) next to it when `account_health_movement` data is available. Label it "trending" — this metric is correlational, not causal. Below: table of other open deals at this account (deal name, amount, stage, risk score) to show the full relationship context. Show total account pipeline value.
- **Value & Expansion Health subsection** (only if `get_value_impact_card` data is available): Add a secondary subsection under the account health showing:
  - Fulfilment score (percentage with color coding)
  - Expansion readiness category (e.g., "Ready for Expansion", "At Risk", "Nurture Track")
  - Evidence confidence indicator
  - This flags expansion risk and opportunity early in the account context.
- **Stakeholder Coverage subsection** (from `opportunity_stakeholder_intelligence`): Add a subsection mapping the buying committee — role, name, engagement level — with coverage gaps called out explicitly (e.g., "No confirmed Economic Buyer", "Champion identified, no VP-level sponsor"). Include the tool's suggested engagement moves as 1-2 short action bullets. This is where the "single-threaded deal" risk flag from Step 3 becomes concrete and actionable. If no data is returned, note "Stakeholder map unavailable" and omit the subsection.
  - **Committee coverage from outreach** (only when Step 2 item 9 confirmed a converted target account): one compact line per buying role — missing / mapped / engaged — with the last-touch date, and the required-role gaps called out ("No economic buyer engaged during outreach; converted 2026-09-02"). Label it **Observed — target-account record, as of [date]** so it is visibly distinct from the stakeholder-intelligence map. Show role names as data, not as a judgment of any person.
- If the account has multiple active deals, this context matters — a problematic deal at a healthy account is different from a problematic deal at a struggling account.
- If no other deals exist, note "Single active deal at this account."

---

#### Slide 9: Value Realization Roadmap (Closed Won deals only)
- **Background**: Off-white (`F8FAFC`)
- **Data source**: `get_value_contract` (only include this slide if the opportunity stage is "Closed Won")
- **Layout**:
  - Title: "Value Realization Roadmap"
  - **Promised Outcomes section**: List each committed outcome from the value contract with:
    - Outcome name (bold)
    - Committed metric or success criteria (1 line)
    - Current status or progress indicator (if available)
  - **Expansion Signals section**: Brief summary of:
    - Whether the customer is tracking toward committed value
    - Early signals of expansion opportunity or renewal risk
  - **Next Steps section**: 2-3 actions needed to protect renewal or unlock expansion, grounded in the promised outcomes
- **Handling missing data**: If `get_value_contract` returns no data for a Closed Won deal, show "No value contract available — reach out to Sales Engineer or Customer Success for details."
- This slide owns the post-sale narrative and surfaces renewal/expansion risk that pure qualification frameworks miss.

---

#### Slide 10: Recommended Next Steps
- **Background**: Off-white (`F8FAFC`)
- **Data source**: Synthesized recommendations from Step 3, plus `prepare_dark_deal_rescue` (conditional appendix — see below)
- **Layout**: 3-5 numbered recommendations, each with:
  - A bold headline action (what to do)
  - A supporting sentence (why, with evidence from the deal data and notes)
- Use numbered circles in emerald as bullet markers. Give each recommendation space.
- Order by impact — the most critical action first.
- Frame as forward-looking actions, not criticisms.
- **Dark Deal Rescue Appendix** (conditional — only if the deal was flagged "going cold" or Red, and `prepare_dark_deal_rescue` is available on this server): Add a clearly-labeled appendix section below the numbered recommendations, headed "APPENDIX: Dark Deal Rescue (Draft — Not Sent)". Include:
  - The overdue-close diagnosis in 1-2 lines
  - Stakeholder gaps identified by the rescue packet
  - The suggested action plan as a short numbered list
  - One line noting that a drafted re-engagement email exists in the packet and that outreach drafting belongs in `deal-action-engine` (if installed) — do not reproduce the email in the deck
  - A prominent label or footer stating this is a **draft for review only** — nothing has been sent or executed. Never phrase this section as something already done.
  - If `prepare_dark_deal_rescue` is unavailable on this connector or the deal doesn't meet the cold/Red trigger, omit this appendix entirely and don't mention it.

---

#### Slide 11: Sources & Limits
- **Background**: Off-white (`F8FAFC`)
- **Content**: a compact two-column list.
  - **Sources**: each tool used, with the as-of / generated timestamp it returned, and which values are tool-provided vs model-derived.
  - **Limits**: every unavailable, empty, stale or contradictory source in one plain line each ("Signal layer: unavailable", "BANT: no data returned", "Health score: 19 days old"). No raw error text, permission messages or access-denied detail.
  - The demo label, if the preflight required one.
- Keep it to one slide at 11-12pt; this is the audit trail, not a talking slide.

---

#### Slide 12: Closing Slide
- **Background**: Navy (`1E2761`)
- **Content**: Deal name, "Prepared for pipeline review", date, "Powered by Summit53"
- **Layout**: Clean, centered. Mirror the title slide design.

---

## Step 5: Generate the File

Write a complete Node.js script using PptxGenJS that:

1. Embeds all the pulled data directly (no external data files)
2. Uses helper functions for repeated patterns (stat cards, colored score cells, risk factor cards, activity timeline entries, outcome cards)
3. Uses factory functions for shadows and styles to avoid PptxGenJS's object mutation issue (create a fresh object each time, never reuse option objects across addShape/addText calls)
4. Constructs all slides following the structure above
5. Handles edge cases (missing data, empty arrays, zero values, null fields, no notes summary, null/empty value contract, missing value impact card)
6. Conditionally includes the Value Realization Roadmap slide only for Closed Won deals
7. Adds the Sources & Limits slide, and the demo label on every slide when the preflight requires it
8. Saves to the session's outputs directory as `Deal-Review-[DealName]-[Date].pptx`

## Step 6: QA

After generating the file:

1. Render every slide to an image using the `pptx` skill's render flow (its `soffice.py` wrapper to PDF, then `pdftoppm` to JPEG). Use the full-resolution renders, not the thumbnail grid.
2. Open and inspect **every slide at full size** for clipping, overlapping text, awkward wrapping, unreadable charts, colour-contrast issues, unresolved placeholders or bracketed TODOs
3. Verify data accuracy — spot-check that numbers match what the MCP tools returned
4. Verify that conditional slides render correctly:
   - For Closed Won deals: confirm Value Realization Roadmap slide is present and properly populated
   - For open deals: confirm Value Realization Roadmap is NOT included
   - For high-ARR accounts: confirm Value & Expansion Health subsection is present on Slide 8
   - For cold/Red deals on a connector where `prepare_dark_deal_rescue` is available: confirm the Dark Deal Rescue appendix is present on Slide 10, clearly labeled as a draft, not an action taken, and contains no email body
   - For healthy deals, or where `prepare_dark_deal_rescue` isn't exposed: confirm the Dark Deal Rescue appendix is correctly omitted
   - Where a competitor was named: confirm the Competitive Positioning callout appears on Slide 4 with real battlecard content, not a placeholder
   - Confirm the Stakeholder Coverage subsection on Slide 8 reflects real coverage gaps, and the account health trend arrow (if shown) is labeled "trending," not "caused by"
   - Confirm the Sources & Limits slide lists every unavailable source and contains no permission or error text
5. Fix issues, re-render the changed slides, and re-inspect them
6. Do not declare success until at least one fix-and-verify cycle is complete
7. Deliver: return **one clickable link** to the final PPTX, followed by a short note on material evidence gaps and anything excluded (fixture rows, unavailable sources). Do not paste the deck content into chat

## Tips for Great Deal Reviews

- **Ground everything in evidence.** Generic statements like "the deal looks risky" are useless. "No champion identified, paper process undefined, and the close date is 12 days away" is actionable. Notes make this even sharper — "the Feb 1 note says procurement is pushing back on price and the last activity was 16 days ago" is a coaching conversation.
- **Let the notes tell the story.** The Deal Narrative slide exists because scores alone don't explain *why* a deal is at risk. If the notes say "competitive bake-off with Clari, pricing pressure from procurement, paper process unresolved" — that's the story. Lead with it.
- **Frame gaps as opportunities, not failures.** "Here's where the biggest upside is hiding" beats "Here's what's wrong."
- **Make the suggested questions specific.** "Who signs the PO at Acme?" beats "Have you identified the economic buyer?"
- **Show the account context.** A $200K deal at an account with $1.5M in other active pipeline gets different treatment than a $200K standalone deal.
- **Keep it tight.** About 11-12 slides including Sources & Limits (12 only if Value Realization is included). The goal is a focused 5-10 minute review, not a deep-dive marathon. Change slide count only when legibility or the evidence demands it.
- **Stay evidence-first.** This is a coaching artifact, not a sales pitch: no causal claims, no invented numbers, and no recommendation that is not traceable to a source.

## Tools Used

This skill pulls data from the following Summit53 tools (logical names; resolve the prefix per the preflight):

- `current_context` — tenant gate; always first
- `list_available_tools` — confirms which optional enhancements this connector exposes
- `get_opportunity` — core deal details and stage
- `search_opportunities` — find deals by name or account; identify related deals at the account
- `risk_heatmap` — deal-level risk scores and risk factors
- `deal_drag_dashboard` — waste scores, staleness, drag causes, recovery strategies
- `get_opportunity_notes_summary` — AI-generated narrative of deal progress (primary source for Deal Narrative slide)
- `get_opportunity_notes` — raw notes as fallback if summary is unavailable
- `get_opportunity_activities` — activity log (calls, emails, meetings, notes) to assess engagement cadence
- `opportunity_framework_summary` — qualification scores (MEDDPIC, BANT, SPICED)
- `account_execution_health` — account-level health score and context
- `activity_gaps` — engagement tracking at the account level
- `get_value_contract` — promised outcomes and expansion signals for Closed Won deals
- `get_value_impact_card` — fulfilment score, expansion readiness, and evidence confidence for high-value accounts
- `get_opportunity_signals` — Revenue Signal Layer: ranked "first constraint to fix," win-probability movement, and evidence-scored signals for the Deal Health Verdict and Blockers slide (access-guarded to leader/owning rep — degrade gracefully if unavailable)
- `prepare_dark_deal_rescue` — shadow-mode rescue packet (diagnosis, stakeholder gaps, drafted re-engagement email, action plan) for deals flagged "going cold" or Red; conditional, evidence only, not exposed on every deployment
- `opportunity_stakeholder_intelligence` — buying-committee map, coverage gaps, and suggested engagement moves for the Stakeholder Coverage subsection
- `get_battlecard` — competitive differentiation talking points, pulled only when a competitor is named in notes or framework evidence
- `account_health_movement` — correlational trend direction (improving/declining) alongside the point-in-time account execution health score
- `search_target_accounts`, `get_target_account` — optional, Outreach plan: committee coverage (mapped/engaged roles, required-role gaps) from the converted outreach target account, matched by `opportunity_id`; read-only

## Guardrails

- Read-only. Never send rescue emails, create notes, write to target accounts or stakeholder suggestions, or execute recommended actions; `prepare_dark_deal_rescue` is shadow-mode evidence only. Writes and outreach hand off to `deal-action-engine` (if installed) only on the user's explicit request.
- Never reveal access-denied detail, permission errors or stack traces inside the deck.
- Never convert missing data into a zero, a green status or a positive signal.
- Never claim causality from activity, framework, account-health or signal correlations.
- Keep tool-provided scores and model-derived judgments visibly separate.
- Preserve the evidence-first coaching posture; do not turn the deck into a generic sales pitch.

## Final verification checklist

- [ ] Preflight checklist complete; `current_context` ran first; returned IDs match `scoped_org_id`
- [ ] Exactly one opportunity resolved, confirmed by the user if the name was ambiguous
- [ ] Health verdict uses `healthBand` / `score_semantics`; stale scores show their age; no inverted `riskScore` thresholds
- [ ] Tool scores and model judgments labelled separately
- [ ] Every unavailable source listed on Sources & Limits, with no access-denied detail
- [ ] No empty result rendered as "no gaps", "no risk" or green
- [ ] Rescue appendix (if present) is labelled draft, evidence only, no email body
- [ ] Target-account coverage used only when `opportunity_id` matched (or the user confirmed); labelled Observed with dates; single-threaded shown as not measured, not 0%
- [ ] Fixture rows excluded, or the demo label is on every slide
- [ ] Every slide rendered and inspected at full size; one link returned
