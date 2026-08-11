---
name: win-loss-analysis
description: "Analyse closed deals to surface what framework scores, activity patterns, and deal characteristics correlate with wins vs losses, then deliver a polished PPTX presentation with data-driven insights. Use this skill whenever anyone asks for a win/loss analysis, win loss report, win rate analysis, deal pattern analysis, closed deal analysis, or any request to understand why deals are won or lost. Also trigger on phrases like 'why are we losing deals', 'what do our wins have in common', 'analyse our closed deals', 'win loss patterns', 'what predicts a win', 'loss reasons', 'deal post-mortem', 'what's working in our sales process', 'show me win vs loss data', 'closed deal review', 'what separates wins from losses', or 'help me understand our win rate'. Even trigger when the user asks broader questions like 'how can we improve our close rate' or 'what should we change about our sales process' — win/loss pattern data is the foundation for answering those questions."
---

> **Codex compatibility notice:** Use this file for cohort logic, evidence requirements, fallbacks, analysis, narrative, slide content, and visual intent. The parent `SKILL.md` overrides every legacy instruction about Claude, PptxGenJS, `pptxgenjs.md`, legacy rendering commands, or a generic outputs folder. Use Codex's available Presentations skill for implementation and QA.

# Win/Loss Pattern Analysis

Analyse closed deals to surface what framework scores, activity patterns, and deal characteristics correlate with wins vs losses. Deliver a polished PPTX presentation with data-driven insights on what's working and what isn't.

## Why This Exists

Every sales org asks "why do we win?" and "why do we lose?" but few have data-driven answers. Reps have anecdotes. Managers have gut feel. This skill replaces both with evidence: it pulls historical deal data from the CRM, slices it by framework scores, deal size, stage velocity, rep performance, and engagement patterns, then surfaces the specific behaviours and characteristics that statistically separate wins from losses. The output is a presentation a sales leader can use to coach the team, adjust the process, or present at an offsite.

## Tools Used

This skill calls the following Summit53 MCP tools in Step 2:
- `risk_heatmap` — deal risk scores and framework scores at close
- `search_opportunities` — won/lost deal list and metadata
- `opportunity_framework_summary` — element-by-element framework scoring for sampled deals
- `get_opportunity_signals` — Revenue Signal Layer for sampled deals: win-probability movement over the deal lifecycle and the flagged first constraint (leader/owning-rep access-guarded)
- `get_opportunity_notes_summary` — AI-generated summary of deal notes
- `get_opportunity_notes` — raw deal notes (for lost deals, especially)
- `get_battlecard` — structured competitor differentiators and objection-handling for competitors named in lost-deal notes
- `get_opportunity` — full deal details, health scores, owner, account linkage
- `get_opportunity_activities` — complete activity log (calls, emails, meetings) for each sampled deal
- `opportunity_stakeholder_intelligence` — buying-committee coverage for sampled deals, used to state a hard multi-threading stat
- `forecast_confidence` — historical forecast accuracy patterns
- `unified_forecast_summary` — canonical win rate by org-adaptive deal-size band (`kpis.win_rate.by_deal_size`); resolve processing envelopes with `get_job` and `references/async-envelopes.md`
- `get_job` — lifecycle polling for `unified_forecast_summary`; re-call the original tool with identical arguments after terminal success
- `arr_growth_analytics` — deal size and ARR context
- `account_intelligence_summary` — account health scores
- `activity_gaps` — account-level engagement recency
- `deal_drag_dashboard` — waste scores and staleness indicators for lost deals
- `deal_drag_summary` — per-deal top qualification gaps, complementing `deal_drag_dashboard`
- `coaching_diagnostic` — Results/Effort/Knowledge/Skills coaching layer used to ground rep-level recommendation language (manager/team-permission gated)

## Step 1: Clarify Scope

Before pulling data, confirm with the user (use sensible defaults if they say "just do it"):

- **Time period**: What range of closed deals? Default to last 12 months / all available data.
- **Company name**: For the title slide. Default to "Summit53" if not specified.
- **Focus**: All deals, or a specific segment (enterprise vs SMB, specific reps, specific stages)? Default to all.
- **Framework preference**: MEDDPIC is the default primary framework. Ask if they also want BANT or SPICED analysis (default: include all three for richer comparison).
- **Audience**: Sales leadership (coaching-focused, operational) or executive (strategic, high-level). Default to sales leadership.

## Step 2: Pull All Data

Call these Summit53 MCP tools. Launch as many in parallel as possible — they're independent. You need a mix of won and lost deal data.

### Required Data Pulls

1. **Won Deals**
   - `risk_heatmap` — filter by stage "Closed Won" if possible, otherwise pull all deals and filter client-side. Get risk scores, framework scores, and risk factors at close. Use a large page_size (50+) to capture enough deals.
   - `search_opportunities` — query with stage "Closed Won", sorted by `updated_at` desc, limit 50. Captures deal names, amounts, close dates, reps, accounts.

2. **Lost Deals**
   - `risk_heatmap` — same approach but for "Closed Lost" deals.
   - `search_opportunities` — query with stage "Closed Lost", sorted by `updated_at` desc, limit 50.

3. **Framework Deep-Dives** (sample both won and lost)
   - For the top 5-8 won deals and top 5-8 lost deals by amount, call `opportunity_framework_summary` with `framework: "MEDDPIC"` for each. This gives you element-by-element comparison data.
   - If time allows (and the user requested it), also pull BANT and SPICED for the same deals.

4. **Deal Narratives** (same sample as framework deep-dives)
   - For each sampled won and lost deal, call `get_opportunity_notes_summary` with the opportunity ID
   - For lost deals specifically, also call `get_opportunity_notes` to surface raw notes — loss reason notes are often the richest source of competitive and objection intelligence
   - When a lost deal's notes name a specific competitor, call `get_battlecard` for that competitor to pull structured differentiators and objection-handling guidance — this enriches the Competitive Intelligence callout on Slide 7 beyond a raw mention count
   - These run in parallel with the framework calls — launch them together
   - The notes are qualitative gold: lost deal notes reveal pricing objections, competitor names, procurement blockers, and exact loss reasons. Won deal notes reveal what actually closed them — champion language, urgency triggers, proof points that landed.

5. **Deal Details & Full Context** (same sample as framework deep-dives)
   - For each sampled won and lost deal (top 5-8 by amount), call `get_opportunity` with the opportunity ID — this retrieves full deal details including health score at close, owner, account linkage, deal history, and current stage
   - Launch these in parallel with the framework and notes calls
   - Use this data to enrich win/loss comparison tables with health scores and rep performance patterns

6. **Deal Activity Sequences** (same sample as framework deep-dives)
   - For each sampled won and lost deal, call `get_opportunity_activities` with the opportunity ID — this pulls the complete activity log (calls, emails, meetings, notes)
   - Launch these in parallel with framework calls — they're independent
   - This is critical data for Slide 8 (Activity & Engagement Patterns) and the new activity-pattern analysis in Step 3e
   - Activity sequences show: (a) total activity volume by type, (b) cadence between touchpoints, (c) last activity type before outcome, (d) engagement momentum patterns (are activities clustered or sparse?)

7. **Revenue Signal Layer** (same sample as framework deep-dives — do not expand beyond the existing 5-8 won / 5-8 lost sample)
   - For each sampled won and lost deal, call `get_opportunity_signals` with the opportunity ID — this returns win-probability movement over the deal's lifecycle and the flagged first constraint (the earliest-detected blocker in the deal's trajectory)
   - Launch these in parallel with the framework, notes, and activity calls — they're independent
   - This is a per-opportunity call, so keep it inside the existing sample batch rather than pulling it for every deal in the pool — cost scales with sample size
   - `get_opportunity_signals` is access-guarded to the leader or owning rep on each opportunity. If a call returns unauthorized or empty for a given deal, skip that deal's signal data and proceed with the rest of the sample — note the reduced count
   - This data is critical for Slide 5 (Predictive Indicators) — it turns "what the score was at close" into "how the trajectory diverged," e.g., lost deals showing a flagged first constraint weeks before the loss

8. **Stakeholder Coverage** (same sample as framework deep-dives — do not expand beyond the existing 5-8 won / 5-8 lost sample)
   - For each sampled won and lost deal, call `opportunity_stakeholder_intelligence` with the opportunity ID — this returns buying-committee coverage: how many stakeholders were engaged, their roles, and engagement depth
   - Launch these in parallel with the other sampled-deal calls
   - This is also a per-opportunity call — keep it inside the existing sample batch, same cost discipline as the signal layer above
   - Use this to replace inferred multi-threading signals (previously read off note text in Step 3d) with a hard stat: e.g., "Won deals averaged 4.6 engaged stakeholders vs 1.8 on losses"

9. **Forecast Accuracy**
   - `forecast_confidence` — historical prediction vs outcome data. Shows how well the forecast model identified eventual wins/losses.

10. **ARR Context**
    - `arr_growth_analytics` — deal size and type patterns, total ARR context. Set `include_trends: true`, `include_benchmarks: true`.

11. **Account Health Patterns**
    - `account_intelligence_summary` — health scores across accounts. Lets you correlate account health with deal outcomes.

12. **Account-Level Activity Patterns**
    - `activity_gaps` — engagement frequency data. Dormant accounts that lost deals vs active accounts that won.
    - `deal_drag_dashboard` filtered to closed-lost stage — for lost deals, check their waste scores and activity levels at the time of loss. "Stalled-then-lost" is a distinct failure pattern (failure to create urgency) vs "lost in active evaluation" (lost on merit). High staleness on lost deals is a coaching signal.
    - `deal_drag_summary` for the same sampled lost deals — pulls per-deal top qualification gaps (the specific MEDDPIC/BANT elements dragging the deal). Use this alongside the dashboard's waste scores to sharpen the active-loss vs stalled-loss segmentation in Step 3e: a stalled-loss with a clear top qualification gap is a coaching target, while an active-loss with strong qualification but high drag points to competitive or pricing pressure instead.

13. **Canonical Win Rate by Deal Size**
    - `unified_forecast_summary` — pull `kpis.win_rate.by_deal_size`. On a processing envelope, poll `get_job` to terminal and re-call the original tool with identical arguments. This is the platform's own win-rate-by-band calculation, computed over org-adaptive deal-size bands (auto-detected from p25/p50/p75 of trailing-12-month closed-won history — not arbitrary brackets). Use it as the canonical band definition for Step 3a and as a cross-check against your own won/lost sample. If your sample's win rate by band diverges sharply from this, note it — it usually means your 50-deal sample window differs from the platform's trailing window. If the band definition remains unavailable, stop and state the missing source; do not substitute hard-coded brackets.

14. **Rep Coaching Grounding** (optional, permission-gated)
    - For each rep represented in the won/lost sample, call `coaching_diagnostic` — this returns the rep's layered Results/Effort/Knowledge/Skills diagnosis, grounding rep-level recommendation language (Step 3f, Slide 10) in an actual diagnostic layer instead of ad hoc pattern-spotting across framework and activity data
    - `coaching_diagnostic` is manager/team-permission gated. If the caller isn't authorized for a rep (or for the team), skip that rep's diagnostic gracefully and fall back to the existing pattern-spotting approach — note the limitation rather than failing the whole pull

### Handling Missing Data

Don't fail if data is sparse — adapt:
- If won or lost deal pools are small (< 5), note "Limited sample size — patterns may not be statistically significant" and proceed with what's available.
- If framework summaries return errors for some deals, skip those deals and note the sample size reduction.
- If forecast confidence data is empty, skip the forecast accuracy slide and note "Forecast history not available."
- If `get_opportunity_signals` is unauthorized or empty for a sampled deal, drop that deal from the signal-layer analysis only — don't drop it from the rest of the sample — and note the reduced count on Slide 5.
- If `coaching_diagnostic` returns a permission error for a rep or the team, skip the coaching-diagnostic grounding for that rep and fall back to pattern-spotting from framework/activity data, noting the gap rather than blocking the deck.
- The analysis gets more powerful with more data. If the user's CRM has limited history, acknowledge it and frame findings as "early signals" rather than "proven patterns."

## Step 3: Analyse and Synthesise

This is the analytical core. Before building slides, crunch the data and write internal findings.

### 3a: Win/Loss Summary Stats

Calculate:
- Overall win rate (won / (won + lost))
- Win rate by deal size band — use the **org-adaptive bands** from `unified_forecast_summary.kpis.win_rate.by_deal_size` (each band carries `rate`, `won`, `total`, and a `label`). These bands are auto-detected from the org's own closed-won history, so they reflect what "small" and "large" actually mean for this business — do not substitute hardcoded brackets like `<$50K / $150K+`. A blended win rate almost always hides a weak band; surfacing the per-band split is the single most actionable cut in this section.
- Win rate by rep (if multiple reps)
- Win rate by stage reached before close (did lost deals stall at a particular stage?)
- Average deal cycle time for wins vs losses

### 3b: Framework Score Comparison

For each framework element (MEDDPIC letters, BANT components, SPICED elements):
- Average score on won deals vs average score on lost deals
- The delta (gap) between win and loss averages
- Rank elements by delta — the biggest gaps are the strongest predictive signals

The elements with the largest win/loss deltas are your "predictive indicators" — they're the framework components that most reliably separate wins from losses.

**Trajectory layer (from `get_opportunity_signals`)**: for the same sampled deals, compare win-probability movement over the deal lifecycle, not just the score at close. Look specifically at the flagged first constraint — the earliest blocker the signal layer detected — and how far before the loss (or win) it appeared. A lost deal with a flagged first constraint 6+ weeks before close is a different failure mode than one flagged in the final week. Where signal data is available, pair each framework delta with "how early did the trajectory diverge" — this is what separates "what was true at close" from "how the deal got there."

### 3c: Risk Factor Patterns

From the risk heatmap data:
- What risk factors appear most frequently on lost deals?
- What risk factors appear on won deals? (Some risk factors may not actually predict loss)
- Average risk score at close for wins vs losses

### 3d: Qualitative Notes Analysis

From the notes summaries and raw notes on sampled deals, surface recurring qualitative patterns:

**Lost deal themes** — scan notes for:
- Competitive mentions (which competitors appear, what concessions they made)
- Objection types (pricing, integration footprint, procurement resistance, timing)
- Stall patterns ("next step is X" appearing in old notes with no follow-through activity)
- Loss reasons stated explicitly vs inferred from context

**Won deal themes** — scan notes for:
- What language appears in champion notes ("confirmed exec approval", "secured tentative sign-off")
- What proof points or counter-arguments closed objections
- What urgency triggers drove the final decision
- Multi-threading signals (notes referencing multiple contacts vs single-threaded deals)

**Hard multi-threading stat (from `opportunity_stakeholder_intelligence`)**: where available, replace the inferred multi-threading signal above with the actual buying-committee coverage number for the sampled deals — e.g., "Won deals averaged 4.6 engaged stakeholders vs 1.8 on losses." This converts an inference from note text into a stated fact for the deck.

**Competitive battlecard enrichment (from `get_battlecard`)**: for any competitor named in lost-deal notes, pull the matching battlecard and note its structured differentiators and objection-handling guidance. Use this to move the Competitive Intelligence callout (Slide 7) beyond "Competitor X mentioned in 3 of 5 losses" toward "Competitor X mentioned in 3 of 5 losses — battlecard flags [differentiator] as the counter; confirm reps used it."

Synthesise these into 2-3 qualitative observations to pair with the quantitative framework findings. Example: "Quantitatively, MEDDPIC Champion scores average 82% on wins vs 31% on losses. Qualitatively, won deal notes consistently mention champion language like 'secured tentative approval' and 'keeping the CRO bought in', while lost deal notes show procurement resistance and single-threaded engagement."

### 3e: Activity & Engagement Patterns (Deal-Level)

Using the `get_opportunity_activities` data from Step 2, calculate engagement patterns for the sampled won vs lost deals:

**Activity Volume Analysis:**
- Count total activities per deal by type: calls, emails, meetings, notes
- Compare average activity counts for won deals vs lost deals
- Example: "Won deals averaged 8.2 total activities (2.3 calls, 3.1 emails, 2.1 meetings) vs lost deals averaged 4.1 activities (0.9 calls, 1.8 emails, 1.2 meetings)"

**Activity Cadence Analysis:**
- For each deal, calculate average days between successive activities (activity frequency)
- Compare cadence for won deals vs lost deals
- Example: "Won deals maintained activity every 5.3 days on average; lost deals showed 12.8-day gaps between touches"

**Last Activity Before Outcome:**
- For each deal, identify the final activity type before close (win/loss decision)
- Segment: Won deals ending with [calls vs emails vs meetings vs notes] — which type of final touch appears most in wins?
- Example: "68% of won deals had a call or meeting in the final 7 days before close vs 22% of lost deals"

**Engagement Momentum:**
- Identify whether activity clustered (burst of engagement near close) or distributed (steady throughout)
- Won deals with clustered final-stage activity vs lost deals with sparse or declining engagement
- Example: "Won deals showed activity acceleration in the final 30 days (8 activities in final month vs 2 in months 1-2); lost deals showed flat or declining engagement through the end"

**Stalled-then-Lost Segmentation (formalized):**
- Segment lost deals explicitly into two categories:
  - **(a) Active-Loss** — lost deals with high activity volume and/or recent engagement (low staleness), indicating competitive loss or merit-based rejection during active evaluation
  - **(b) Stalled-Loss** — lost deals with low activity volume and/or long gaps before final loss (high staleness), indicating failure to maintain momentum and urgency
- Use `deal_drag_dashboard` waste scores or activity recency from `get_opportunity_activities` as segmentation criteria
- Tailor loss-reason analysis and recommendations to each segment (see Slides 9 and 10 below)
- Where available, use `deal_drag_summary`'s per-deal top qualification gap alongside the waste score — a stalled-loss with a named top gap (e.g., missing Economic Buyer) is a coaching target; an active-loss with a clean qualification profile but high drag points toward competitive or pricing pressure instead

### 3f: Actionable Recommendations

Based on the analysis, generate 5-7 specific, evidence-backed recommendations:
- Each recommendation should cite the specific data pattern that supports it
- Frame as forward-looking actions ("Focus discovery calls on identifying the economic buyer — deals with EB scores above 70% close at 3x the rate of those below 30%")
- Order by expected impact
- **For stalled-losses**, recommend urgency-creation actions: "Implement a Stage 2 → Stage 3 momentum checkpoint — require evidence of at least one stakeholder meeting in the past 10 days"
- **For active-losses**, recommend differentiation or qualification actions: "Conduct post-loss win/loss calls on competitive losses to refine positioning on the top 2 product differentiators"
- Ground recommendations in the combination of framework gaps, health-score patterns, and activity cadence data
- Where `coaching_diagnostic` data is available and authorized for a rep, ground that rep's recommendation in their actual Results/Effort/Knowledge/Skills layer rather than inferring the cause from framework/activity data alone — e.g., "Rep X's coaching diagnostic flags a Knowledge gap on discovery questioning, consistent with their below-average Champion scores." If unauthorized, fall back to the pattern-spotting approach already described above.

### 3g: Headline Narrative

Write a one-sentence headline that captures the analysis story:
- "Champion identification is the #1 predictor of winning — deals with strong champions close at 4x the rate"
- "We're losing on Paper Process: 78% of losses had undefined procurement paths"
- "Engagement matters: won deals had 3x more touchpoints in the final 30 days"

## Step 4: Build the Deck

Read the pptx skill's `pptxgenjs.md` reference for technical details of creating slides with PptxGenJS.

### Design System

Use the **Cherry Bold** palette — this is an analytical/diagnostic deck, not a boardroom update. The bold red gives it urgency and distinguishes it from operational decks:

| Role | Color | Hex |
|------|-------|-----|
| Primary (dark backgrounds) | Cherry | `990011` |
| Secondary (light backgrounds) | Off-white | `FCF6F5` |
| Accent | Navy | `2F3C7E` |
| Positive / Win | Emerald | `10B981` |
| Negative / Loss | Cherry Red | `990011` |
| Warning | Amber | `F59E0B` |
| Text on dark | White | `FFFFFF` |
| Text on light | Charcoal | `1E293B` |
| Light background | Off-white | `FCF6F5` |
| Subtle border | Slate | `64748B` |
| Muted text | Slate | `94A3B8` |

**Typography**: Georgia headers (36-44pt), Calibri body (14-16pt).
**Layout**: 16:9 widescreen. 0.5" margins minimum. Dark title/close slides, light content slides.

### Slide Structure (11 Slides)

---

#### Slide 1: Title Slide
- **Background**: Cherry (`990011`)
- **Content**: Company name, "Win/Loss Pattern Analysis", time period covered (e.g., "Last 12 Months"), date generated
- **Layout**: Centered, clean. Large Georgia title in white, smaller Calibri subtitle in off-white.

---

#### Slide 2: Executive Summary
- **Background**: Cherry (`990011`)
- **Content**: The headline narrative from Step 3g as a large quote-style callout (28-32pt, white). Below: 3 key findings as compact bullet-style statements (16-18pt, off-white).
- **This slide answers**: "What's the one thing we should take away from this analysis?"

---

#### Slide 3: Win/Loss Summary
- **Background**: Off-white (`FCF6F5`)
- **Data source**: Calculated stats from Step 3a, with health-score-at-close from Step 2 `get_opportunity` calls
- **Layout**: Top row — 4 stat cards: Overall Win Rate (%), Total Won Deals, Total Lost Deals, Average Deal Size (won vs lost side by side). Below: bar chart showing win rate by deal size bracket. Use emerald for wins, cherry for losses throughout.
- **Stat card design**: Value in 28-32pt bold, label below in 11-12pt muted. Cards ~2.2" wide with navy left-border accents.
- **Enrichment**: If health scores are available, add a secondary comparison table showing average health score at close for won deals vs lost deals — this is a leading indicator of deal quality. Example: "Avg. health score at close — Won: 78% | Lost: 41%"

---

#### Slide 4: Framework Score Comparison (MEDDPIC)
- **Background**: Off-white (`FCF6F5`)
- **Data source**: Framework averages from Step 3b
- **Layout**: Horizontal grouped bar chart — one bar pair per MEDDPIC element (M, E, D, D, I, C, P). Green bars for won-deal averages, red bars for lost-deal averages. This visual makes the gaps immediately obvious.
- **Below the chart**: Callout card highlighting the #1 predictive element (largest gap) with a one-sentence insight.
- **If framework data is limited**: Use a table layout instead — element name, win average, loss average, delta, with color-coded delta column.

---

#### Slide 5: Predictive Indicators
- **Background**: Off-white (`FCF6F5`)
- **Data source**: Ranked framework elements from Step 3b, enriched with win-probability movement and flagged first constraints from `get_opportunity_signals` (Step 3b trajectory layer)
- **Layout**: Ranked list of the top 5 framework elements by win/loss delta. Each item shown as a card with:
  - Element name (bold)
  - Win avg score → Loss avg score (with arrow and delta)
  - One-line interpretation ("Deals with strong Champions close at X% vs Y% without")
- Use navy numbered circles (1-5) as rank markers. Colour the delta values: emerald if the gap favours wins meaningfully, red if a low score is strongly associated with loss.
- Where signal data is available, add a trajectory strip beneath the ranked list: a compact mini-timeline or callout showing how many weeks before loss the flagged first constraint typically appeared (e.g., "Lost deals show a flagged constraint an average of 5.4 weeks before close — often before the deal even reaches late-stage forecasting"). This turns the slide from static scores into a trajectory story.
- **This is the "money slide"** — it tells the team exactly where to focus coaching and qualification effort.

---

#### Slide 6: BANT & SPICED Comparison
- **Background**: Off-white (`FCF6F5`)
- **Data source**: BANT and SPICED framework averages from Step 3b
- **Layout**: Two-column layout. Left: BANT elements (Budget, Authority, Need, Timeline) with win vs loss averages shown as side-by-side mini-bars or a compact table. Right: SPICED elements (Situation, Pain, Impact, Critical Event, Decision) same treatment.
- Colour-code each score: emerald ≥ 70%, amber 40-69%, red < 40%.
- If only one framework is available, use the full width for it.
- **If neither is available**: Skip this slide entirely.

---

#### Slide 7: What the Field Is Saying (Qualitative Themes)
- **Background**: Off-white (`FCF6F5`)
- **Data source**: Notes summaries and raw notes from Step 3d qualitative analysis, hard stakeholder-coverage stats from `opportunity_stakeholder_intelligence`, and battlecard enrichment from `get_battlecard`
- **Layout**: Two-column layout — "Why We Win" (emerald left-border cards) on the left, "Why We Lose" (cherry left-border cards) on the right.
  - Each card has a theme name (bold) and 1-2 lines of evidence drawn from actual notes (paraphrased, not verbatim). Example: "Champion Language — Won deal notes consistently reference executive sponsorship confirmed and CRO buy-in secured."
  - Show 3-4 cards per column.
- If `opportunity_stakeholder_intelligence` data was pulled (Step 3d), add a small stat line above or beside the two columns: "Won deals averaged X engaged stakeholders vs Y on losses" — a hard number that anchors the multi-threading theme instead of leaving it as an inferred note-text pattern.
- Below: a "Competitive Intelligence" callout if competitor names or concessions appeared in lost deal notes (e.g., "Clari mentioned in 3 of 5 sampled losses — price concessions and integration footprint cited"). If a matching `get_battlecard` was pulled for that competitor (Step 3d), enrich the callout with 1-2 structured differentiators or objection-handling points from the battlecard rather than just the note-derived mention count.
- This slide bridges the quantitative framework data with the human reality of what's happening in the field.
- If notes data is sparse, reduce to a single column of observations and note the limited sample.

---

#### Slide 8: Activity & Engagement Patterns
- **Background**: Off-white (`FCF6F5`)
- **Data source**: Deal-level activity sequences from Step 3e (`get_opportunity_activities` data), account-level activity gaps from `activity_gaps`, and deal_drag_dashboard / `deal_drag_summary` for stalled-vs-active loss segmentation
- **Layout**: Three-section layout:
  1. **Deal Activity Volume** (top) — stat callouts comparing average activity counts by type. Example cards: "Won deals: 8.2 avg activities (2.3 calls, 3.1 emails, 2.1 mtgs)" vs "Lost deals: 4.1 avg activities (0.9 calls, 1.8 emails, 1.2 mtgs)". Use emerald for won, cherry for lost.
  2. **Activity Cadence** (middle) — stat callout showing average days between activities. Example: "Won deals: 5.3-day cadence | Lost deals: 12.8-day cadence" with visual gap indicator (emerald gap for wins = tight cadence, red gap for losses = sparse).
  3. **Final Activity Type Before Close** (bottom) — small horizontal bar chart or icon row showing which activity type appeared most in the final 7 days before outcome. Example: "68% of wins ended with call/meeting; 22% of losses did."
- **Key insight to surface**: Engagement frequency and momentum directly correlate with wins. Frame as actionable: "Won deals averaged touches every 5+ days; lost deals showed 13-day gaps. Tighter cadence predicts wins at 2.5x the rate."
- Include a callout box noting the stalled-vs-active segmentation if relevant: "Of X lost deals, Y were active-losses (competitive) and Z were stalled-losses (momentum failure)." Where `deal_drag_summary` is available, add the most common named top qualification gap for the stalled-loss group (e.g., "...the most common named gap on stalled-losses was Economic Buyer access.").
- If activity data is limited, show what's available and note the limitation.

---

#### Slide 9: Common Loss Reasons
- **Background**: Off-white (`FCF6F5`)
- **Data source**: Risk factor patterns from Step 3c, qualitative themes from Step 3d, loss segmentation from Step 3e, and per-deal qualification gaps from `deal_drag_summary`
- **Layout**: Loss patterns shown as cards with a cherry-red left border. Card contains:
  - Loss pattern name (bold, e.g., "No Economic Buyer Access")
  - Loss type tag (small badge): "Active Loss" (emerald tag) or "Stalled Loss" (amber tag) — indicates whether this was a competitive/merit loss or a momentum failure
  - Frequency (appeared in X% of lost deals)
  - One-line description with evidence — blend quantitative (risk factor frequency, activity data) with qualitative (what the notes say) where available
- Limit to top 5-6 patterns. Arrange in a 2-column grid or vertical stack.
- **Segmentation signal**: Group or visually separate active-loss patterns from stalled-loss patterns so coaching responses are tailored (differentiation for active-losses vs urgency for stalled-losses)
- Where `deal_drag_summary` names a specific top qualification gap shared across multiple stalled-loss deals, surface it as its own pattern card rather than folding it into a generic "lost momentum" bucket — the named gap is more actionable.
- **This is the diagnostic slide** — it names the specific failure modes, categorized by loss type, so the team can address them appropriately.

---

#### Slide 10: Actionable Recommendations
- **Background**: Off-white (`FCF6F5`)
- **Data source**: Synthesised recommendations from Step 3f, informed by health scores, activity patterns, loss segmentation, and — where authorized — `coaching_diagnostic`
- **Layout**: 5-7 numbered recommendations, each with:
  - Bold action headline (what to do)
  - Supporting evidence (which data pattern supports this, cited specifically — quantitative and qualitative)
  - Loss-type callout (if applicable): **For Stalled-Losses**, **For Active-Losses**, or **For All Losses** — to indicate which failure mode this recommendation addresses
- Use navy numbered circles as markers. Give each recommendation breathing room.
- Order by expected impact — the highest-leverage action first.
- Frame recommendations as process improvements, not blame: "Add a Champion validation checkpoint at Stage 3" rather than "Reps aren't identifying champions."
- **Include stalled-vs-active differentiation**:
  - Recommendations for stalled-losses emphasize urgency creation, momentum, and cadence: "Implement a 7-day max-gap rule between activities — any deal with >7 days idle triggers an escalation review."
  - Recommendations for active-losses emphasize competitive differentiation, qualification depth, and positioning: "In Stage 2 discovery, add a mandatory competitive positioning question to understand how we stack up in the buyer's mind."
- **Incorporate rep-level patterns** where data allows: "Rep X's deals show strong framework scores but lower activity volume — focus coaching on maintaining post-initial-discovery cadence" or "Rep Y's won deals average 2.8 calls in the final 30 days vs team average 1.9 — use as model for other reps." Where `coaching_diagnostic` is available and authorized for a rep, cite the specific Results/Effort/Knowledge/Skills layer it flags rather than inferring the cause from framework/activity data alone — e.g., "Rep X's coaching diagnostic flags a Skills gap on multi-threading; pair with the stakeholder-coverage data above." If unauthorized, keep the existing pattern-spotting language.

---

#### Slide 11: Closing Slide
- **Background**: Cherry (`990011`)
- **Content**: Company name, "Data-driven insights to improve win rates", date, "Powered by Summit53"
- **Layout**: Clean, centered. Mirror the title slide design.

---

### Chart Generation

Prefer native PptxGenJS charts (BAR, DOUGHNUT, PIE) — they're editable in PowerPoint. Match chart colours to the palette. Use the styling guidance from pptxgenjs.md (custom colours, clean backgrounds, muted axis labels, subtle grid lines).

For the framework comparison chart (Slide 4), a grouped bar chart works well natively in PptxGenJS — use two data series (Won, Lost) with `barDir: 'col'` and colour them emerald and cherry respectively.

## Step 5: Generate the File

Write a complete Node.js script using PptxGenJS that:

1. Embeds all the pulled and calculated data directly (no external data files)
2. Uses helper functions for repeated patterns (stat cards, risk cards, comparison bars)
3. Uses factory functions for shadows and styles to avoid PptxGenJS's object mutation issue (create a fresh object each time, never reuse option objects across addShape/addText calls)
4. Constructs all slides following the structure above
5. Handles edge cases (missing data, empty arrays, zero values, null fields, small sample sizes)
6. Saves to the outputs folder as `Win-Loss-Analysis-[CompanyName]-[Date].pptx`

## Step 6: QA

After generating the file:

1. Convert to images:
   ```bash
   python scripts/office/soffice.py --headless --convert-to pdf output.pptx
   pdftoppm -jpeg -r 150 output.pdf slide
   ```
2. Visually inspect every slide for overlapping text, missing data, colour contrast issues
3. Verify data accuracy — spot-check that numbers match what the MCP tools returned
4. Fix issues and re-verify
5. Do not declare success until at least one fix-and-verify cycle is complete

## Tips for Great Win/Loss Analysis

- **Let the data tell the story.** Resist the urge to editorialise beyond what the data supports. If the sample is small, say so.
- **Compare, don't just describe.** "Champion scores average 72% on wins" is weak. "Champion scores average 72% on wins vs 28% on losses — a 44-point gap that makes it the #1 predictor" is actionable.
- **Make recommendations specific and forward-looking.** "Improve qualification" is useless. "Add a mandatory Champion validation question to the Stage 2 exit criteria" is implementable.
- **Acknowledge limitations.** Small sample sizes, missing frameworks, and incomplete data are all OK — but the audience needs to know so they calibrate confidence appropriately.
- **Frame losses as learning opportunities.** The tone should be curiosity ("what can we learn?") not blame ("who messed up?"). The goal is process improvement, not finger-pointing.
