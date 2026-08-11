---
name: deal-review-prep
description: "Generate a deal review prep deck as a polished PPTX presentation for a specific opportunity. Pulls qualification framework scores (MEDDPIC/BANT/SPICED), risk heatmap data, account execution health, and activity gaps from Summit53 CRM tools to produce a structured one-pager with everything needed to coach a rep or review a deal in a pipeline review meeting. Use this skill whenever anyone asks to prep for a deal review, review a specific deal, prepare for a pipeline review meeting, do a deal deep-dive, generate a deal scorecard, assess deal health, or analyze a specific opportunity. Also trigger on phrases like 'review this deal', 'deal prep for [deal name]', 'how healthy is the [deal] deal', 'prep me for pipeline review', 'what's the risk on [deal]', 'deal review for opportunity [ID]', 'is this deal going to close', 'should I be worried about [deal]', or 'give me the full picture on [deal]'."
---

> **Codex compatibility notice:** Use this file for domain logic, evidence requirements, fallbacks, narrative, slide content, and visual intent. The parent `SKILL.md` overrides every legacy instruction about Claude, PptxGenJS, `pptxgenjs.md`, `soffice.py`, `pdftoppm`, or a generic outputs folder. Use Codex's available Presentations skill for implementation and QA.

# Deal Review Prep

Generate a structured, coaching-ready deal review deck for a specific opportunity by pulling live data from Summit53 CRM tools and assembling it into a polished PPTX presentation. This is the "everything you need in 30 seconds" prep for pipeline review meetings and 1:1 coaching.

## Why This Exists

Before every pipeline review, managers scramble to pull deal data, cross-reference qualification frameworks, and figure out the right questions to ask. AEs scramble to make sure they have answers. This skill does it in one shot: live CRM data flows into a professional deal review deck with specific risk factors, framework gaps, and suggested coaching questions. It turns a deal number into a coaching conversation.

## Step 1: Identify the Deal

You need an opportunity ID. If the user provides one, call `get_opportunity` directly with it — this is the fastest and most complete path, returning health score, final amount, contract term, and discount fields that `search_opportunities` doesn't expose.

If they give you a deal name or account name instead:

1. Call `search_opportunities` with the deal or account name as the query
2. If multiple results come back, show them and ask the user to pick one
3. Once you have the opportunity ID, call `get_opportunity` to get the full deal record
4. Note the account ID from the result (you'll need it for account context)

If the user says something like "review my biggest deal" or "look at the riskiest deal", use `risk_heatmap` or `search_opportunities` sorted appropriately to find it, confirm with the user, then call `get_opportunity` to fetch full details.

## Step 2: Pull All Data

Launch these calls in parallel where possible — they're mostly independent. You need the opportunity ID and account ID from Step 1.

### Required Data Pulls

1. **Deal Details & Risk**
   - `get_opportunity` with the opportunity ID — the primary deal record: name, amount, stage, close date, forecast category, rep, health score, final amount, contract term, discount. Use this instead of `search_opportunities` for single-deal lookups.
   - `risk_heatmap` filtered to find this specific deal — `healthScore`, `healthBand`, score freshness, and risk-factor breakdown. Treat `score_semantics` as authoritative: higher health is better and `riskScore` is only a deprecated alias.
   - `deal_drag_dashboard` filtered to this deal (use `min_score: 0` to capture all deals, then find this opportunity by ID) — waste score, staleness %, activity level, drag cause, and recovery strategy. A deal can have a moderate risk score but a high waste score if it has been stalled for weeks — this gives the complementary "cost of inaction" view.
   - `get_opportunity_signals` with the opportunity ID — the Revenue Signal Layer: a single ranked "first constraint to fix," win-probability movement, and evidence-scored signals. **Access-guarded** (leader/owning rep only) — always attempt the call, but if it returns an access-denied error or empty result, degrade gracefully and fall back to the hand-derived verdict from risk + framework scores in Step 3. Never let this block deck generation.

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
   - `prepare_dark_deal_rescue` with the opportunity ID — a shadow-mode rescue packet: overdue-close diagnosis, stakeholder gaps, a drafted re-engagement email, and a suggested action plan. This tool is **read-only/shadow-mode** — it drafts, it does not send or execute anything. Treat everything it returns as a draft for the rep/manager to review, never as an action already taken.
   - **Deployment note**: `prepare_dark_deal_rescue` currently exists on the Summit53 STAGING server only, not Prod. Check availability before calling; if it's unavailable (e.g., on Prod), skip the call entirely and skip the rescue appendix on Slide 10 — don't error or block deck generation.

8. **Competitive Battlecard** (conditional — only if the notes summary or framework evidence names a specific competitor)
   - `get_battlecard` for the named competitor — differentiation talking points and positioning guidance. Powers the Competitive Positioning callout on Slide 4. Skip entirely if no competitor is named anywhere in the pulled data.

### Handling Missing Data

Don't fail if data is sparse — adapt:
- If `get_opportunity_notes_summary` returns no summary, pull the 3 most recent raw notes from `get_opportunity_notes` as a fallback for the Narrative slide. Render as bullet points and label as "Recent Notes (summary unavailable)" to distinguish from the AI summary.
- If `get_opportunity_activities` returns empty, note "No activities logged on this deal"
- If a framework summary returns an error or empty data, skip that framework and note "Framework data unavailable"
- If account execution health is empty, note "No account health data available" and move on
- If activity gaps returns nothing for this account, that's actually good — note "No engagement gaps detected"
- If `get_value_impact_card` returns no data, skip the Value & Expansion Health subsection on Slide 8
- If `get_value_contract` returns no data for a Closed Won deal, note "No value contract available" on the Value Realization slide
- If `get_opportunity_signals` is inaccessible (access-guarded to leader/owning rep) or returns empty, fall back silently to the hand-derived Deal Health Verdict from risk + framework scores — don't surface an error to the user
- If `prepare_dark_deal_rescue` is unavailable (not deployed on this server) or the deal doesn't meet the cold/Red condition, skip the Dark Deal Rescue appendix on Slide 10 entirely
- If `opportunity_stakeholder_intelligence` returns no data, note "Stakeholder map unavailable" on Slide 8 and skip the coverage-gap callouts
- If `get_battlecard` returns no match for the named competitor, skip the Competitive Positioning callout on Slide 4
- If `account_health_movement` returns no trend data, show the point-in-time `account_execution_health` score alone, with no trend arrow
- The deal might be new with limited data — that's fine, the deck will just be lighter

## Step 3: Analyze and Synthesize

Before building slides, synthesize the raw data into actionable coaching insights. This is what makes the deck useful.

### Deal Health Assessment

Look at the server-supplied `healthBand` and framework scores together to create a one-line deal health verdict:
- **Green (Healthy)**: `healthBand: High` and MEDDPIC average > 70%. "This deal is well-qualified and on track."
- **Yellow (Needs Attention)**: `healthBand: Medium`, or MEDDPIC average 40-69%. "Winnable, but gaps need closing."
- **Red (At Risk)**: `healthBand: Low`, or MEDDPIC average < 40%. "Significant risk — needs intervention this week."

If `healthBand` is absent, derive only from the response's declared `score_semantics`; do not apply inverted thresholds to `riskScore`. If the score is stale, show its age next to the verdict and reduce its evidentiary weight.

Cross-reference the health verdict against the notes summary. If the notes describe competitive threats, pricing pressure, procurement resistance, or stalled next steps, escalate the health rating accordingly even if the quantitative scores look acceptable.

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

If this assessment flags the deal "Going cold," or the Deal Health Assessment above lands on Red, that's the trigger to pull `prepare_dark_deal_rescue` (Step 2, item 7) and build the Dark Deal Rescue appendix on Slide 10. Cross-check the single-threaded flag against `opportunity_stakeholder_intelligence`'s coverage gaps — a "concentrated on one person" read from activities and a missing economic buyer from stakeholder intelligence are the same underlying risk seen two ways.

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

Read the pptx skill's `pptxgenjs.md` reference for PptxGenJS technical details. Use the **Midnight Executive** design system for visual consistency with other Summit53 deliverables.

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
- Below the cards: a one-line "Deal Health Verdict" from your synthesis in Step 3, using a colored background strip matching the health band (emerald/amber/red). When `get_opportunity_signals` is available, lead the verdict with its ranked "first constraint to fix" and note the win-probability movement (e.g., "First constraint: no economic buyer confirmed — win probability trending down") instead of a generic framework label; otherwise use the hand-derived verdict. If the waste score is high (≥ 26) while `healthBand` is `Medium` or `High`, call this out explicitly: "Deal stalled — high staleness despite a non-low health band."
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
- If there are no risk factors, show an emerald "No risk factors detected" callout — this is a positive signal worth highlighting.

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
- If no blockers: show an emerald callout "No critical blockers detected — deal is well-qualified."

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
  - The drafted re-engagement email, shown as a preview block (not editable in the deck, just visible)
  - The suggested action plan as a short numbered list
  - A prominent label or footer stating this is a **draft for review only** — nothing has been sent or executed. Never phrase this section as something already done.
  - If `prepare_dark_deal_rescue` is unavailable on this server (e.g., Prod) or the deal doesn't meet the cold/Red trigger, omit this appendix entirely and don't mention it.

---

#### Slide 11: Closing Slide
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
7. Saves to the outputs folder as `Deal-Review-[DealName]-[Date].pptx`

## Step 6: QA

After generating the file:

1. Convert to images:
   ```bash
   python scripts/office/soffice.py --headless --convert-to pdf output.pptx
   pdftoppm -jpeg -r 150 output.pdf slide
   ```
2. Visually inspect every slide for overlapping text, missing data, color contrast issues
3. Verify data accuracy — spot-check that numbers match what the MCP tools returned
4. Verify that conditional slides render correctly:
   - For Closed Won deals: confirm Value Realization Roadmap slide is present and properly populated
   - For open deals: confirm Value Realization Roadmap is NOT included
   - For high-ARR accounts: confirm Value & Expansion Health subsection is present on Slide 8
   - For cold/Red deals on a server where `prepare_dark_deal_rescue` is available: confirm the Dark Deal Rescue appendix is present on Slide 10 and clearly labeled as a draft, not an action taken
   - For healthy deals, or on Prod where `prepare_dark_deal_rescue` doesn't exist: confirm the Dark Deal Rescue appendix is correctly omitted
   - Where a competitor was named: confirm the Competitive Positioning callout appears on Slide 4 with real battlecard content, not a placeholder
   - Confirm the Stakeholder Coverage subsection on Slide 8 reflects real coverage gaps, and the account health trend arrow (if shown) is labeled "trending," not "caused by"
5. Fix issues and re-verify
6. Do not declare success until at least one fix-and-verify cycle is complete

## Tips for Great Deal Reviews

- **Ground everything in evidence.** Generic statements like "the deal looks risky" are useless. "No champion identified, paper process undefined, and the close date is 12 days away" is actionable. Notes make this even sharper — "the Feb 1 note says procurement is pushing back on price and the last activity was 16 days ago" is a coaching conversation.
- **Let the notes tell the story.** The Deal Narrative slide exists because scores alone don't explain *why* a deal is at risk. If the notes say "competitive bake-off with Clari, pricing pressure from procurement, paper process unresolved" — that's the story. Lead with it.
- **Frame gaps as opportunities, not failures.** "Here's where the biggest upside is hiding" beats "Here's what's wrong."
- **Make the suggested questions specific.** "Who signs the PO at Acme?" beats "Have you identified the economic buyer?"
- **Show the account context.** A $200K deal at an account with $1.5M in other active pipeline gets different treatment than a $200K standalone deal.
- **Keep it tight.** 10-11 slides max (11 only if Value Realization is included). The goal is a focused 5-10 minute review, not a deep-dive marathon.

## Tools Used

This skill pulls data from the following Summit53 CRM tools:

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
- `prepare_dark_deal_rescue` — shadow-mode rescue packet (diagnosis, stakeholder gaps, drafted re-engagement email, action plan) for deals flagged "going cold" or Red; conditional, and currently STAGING-only (not on Prod)
- `opportunity_stakeholder_intelligence` — buying-committee map, coverage gaps, and suggested engagement moves for the Stakeholder Coverage subsection
- `get_battlecard` — competitive differentiation talking points, pulled only when a competitor is named in notes or framework evidence
- `account_health_movement` — correlational trend direction (improving/declining) alongside the point-in-time account execution health score
