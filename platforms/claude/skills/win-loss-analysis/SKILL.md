---
name: "win-loss-analysis"
description: "Analyse a cohort of closed Summit53 deals and build a win/loss PPTX: outcome rates with denominators, framework, activity and stakeholder patterns associated with wins and losses, coded qualitative themes with deal counts, loss patterns, segment differences, and recommendations framed as measurable validation tests. For sales leaders, RevOps and offsites. Use for win/loss reports, win-rate analysis, closed-deal analysis, deal post-mortems, 'why are we losing deals', 'what do our wins have in common', 'what separates wins from losses', 'what predicts a win', 'loss reasons', 'win loss patterns', 'help me understand our win rate', 'how can we improve our close rate'. Do not use for a live competitor in an active deal — use competitor-response-card. Do not use for individual rep coaching — use rep-coaching-report."
version: "1.1.0"
baselined: "2026-10-13"
status: "active"
---

# Win/Loss Pattern Analysis

Analyse a reproducible cohort of closed deals to show which framework scores, activity patterns and deal characteristics are **associated** with wins vs losses, and deliver a polished PPTX that separates observed associations from causal claims.

## Why this exists

Every sales org asks "why do we win?" and "why do we lose?", but few have evidence-based answers. Reps have anecdotes; managers have gut feel. This skill pulls closed-deal history from the CRM, slices it by framework scores, deal size, stage history, engagement and stakeholder coverage, and surfaces the patterns that differ between wins and losses. The output is a deck a sales leader can use to set coaching priorities, adjust process, or run an offsite — with every pattern shown alongside its sample size so the audience can calibrate confidence.

**Correlation is not a predictor without out-of-sample validation.** A pattern found in this cohort is an association. It becomes a predictor only after it holds on deals it was not derived from, which is why recommendations are written as validation tests.

## Route first

- A live competitor in an active deal → `competitor-response-card`.
- Coaching an individual rep → `rep-coaching-report`.
- Portfolio and historical competitive patterns across closed deals stay here.

## Preflight

Read [references/connector-preflight.md](references/connector-preflight.md) and complete its checklist before any data call. If the tools below are deferred, load them in one ToolSearch `select:` call.

Skill-specific gates:

- **Demo label.** Commercial artifact: if fixture rows cannot be separated, label the whole deck **Demo data — not for customer or commercial decisions**.
- **Cohort defined** (Step 1) before any rate is computed: closed-date window, outcome stages that count as won and lost, currency, segment filters.
- **Read-only.** No `refresh`, no notes, no writes.
- **Missing source stop.** If the canonical deal-size band definition from `unified_forecast_summary` remains unavailable after the async flow, stop and state the missing source (see Step 2, item 13).

Read [references/async-envelopes.md](references/async-envelopes.md) before calling `unified_forecast_summary`; it can return a processing envelope that is not data.

## Tools used

Inspect each live schema before the first call; argument names below are semantic guidance.

- `search_opportunities` — won/lost deal list and metadata (cohort source)
- `risk_heatmap` — deal `healthScore` (0.0–1.0, higher = healthier), `healthBand`, framework scores and risk factors; paginated
- `opportunity_framework_summary` — element-by-element framework scoring for sampled deals
- `get_opportunity_signals` — win-probability movement and the flagged first constraint for sampled deals (access-guarded to leader / owning rep)
- `get_opportunity_notes_summary` — AI summary of deal notes
- `get_opportunity_notes` — raw deal notes (especially lost deals)
- `get_battlecard` — differentiators and objection handling for competitors named in lost-deal notes
- `get_opportunity` — full deal details, health, owner, account linkage, stage history
- `get_opportunity_activities` — activity log (calls, emails, meetings) per sampled deal
- `opportunity_stakeholder_intelligence` — buying-committee coverage per sampled deal
- `forecast_confidence` — historical forecast accuracy patterns
- `unified_forecast_summary` — canonical win rate by org-adaptive deal-size band (`kpis.win_rate.by_deal_size`)
- `get_job` — lifecycle polling for `unified_forecast_summary`; re-call the original tool with identical arguments after terminal success
- `arr_growth_analytics` — deal size and ARR context
- `account_intelligence_summary` — account health
- `activity_gaps` — account-level engagement recency
- `deal_drag_dashboard` — waste scores and staleness for lost deals
- `deal_drag_summary` — per-deal top qualification gaps
- `coaching_diagnostic` — Results/Effort/Knowledge/Skills layer for rep-level recommendation language (manager/team-permission gated)

## Step 1: Clarify scope and define the cohort

Confirm with the user (use defaults if they say "just do it"):

- **Closed-date window**: default last 12 months.
- **Company name** for the title slide: default to the organization name from `current_context`.
- **Focus**: all deals or a segment (deal size, motion, region, rep team). Default: all.
- **Framework**: MEDDPIC primary; include BANT and SPICED by default for comparison.
- **Currency**: the org's reporting currency.
- **Audience**: sales leadership (operational) or executive (strategic). Default: sales leadership.

Write down the cohort definition before pulling data: which stage names count as **won**, which as **lost**, the closed-date window, currency, and any segment filters. Every rate in the deck refers back to this definition.

## Step 2: Pull the data

### Build the cohort (complete, or disclose truncation)

1. **Won and lost lists.** `search_opportunities` with the won stage, then the lost stage. Its live schema exposes `limit` but no page or offset, and sorts by `updated_at` by default. Retrieve the cohort in **bounded windows**: if a call returns exactly `limit` rows, treat it as possibly truncated and split it into value bands with `min_value` / `max_value` (and/or reverse `sort_direction`), re-querying each band until every window returns fewer than `limit` rows. Cap the effort at about 10 windows per outcome. Filter by closed date client-side.
2. **Deal health and framework at close.** `risk_heatmap` with the won and lost stages (or unfiltered and filtered client-side if stage filtering is unsupported), plus the close-date window where the schema allows. It paginates: read `total` on the first page and page until every row is retrieved. `healthScore` is higher-is-healthier; `riskScore` is a deprecated alias with the same direction.
3. **Reconcile** the two sources by opportunity ID.
4. **If the cohort cannot be completed** within the bounded windows, do not present a partial list as the whole. Record "Cohort truncated: {n_won} won and {n_lost} lost retrieved; true totals unknown (or {total} per `risk_heatmap`)" and carry it onto Slide 3 and the closing limits.

### Clean the cohort

Exclude, and count each exclusion for the limits section:

- **Open** deals (any non-closed stage) and deals closed outside the window.
- **Duplicates** (same opportunity under two IDs, or the same deal re-created after a stage reset — keep one).
- **Deleted or archived** records.
- **Incomparable** records: different currency without a conversion, renewals mixed into a new-business cohort (unless the user asked for both and they are segmented), no-decision/withdrawn outcomes unless the cohort definition includes them explicitly.
- **Fixture rows** per the preflight.

### Sample deep-dives (batched)

Choose the sample: the top 5–8 won and top 5–8 lost deals by amount from the cleaned cohort (state the selection rule; it skews to large deals). For each sampled deal, call the per-deal tools below in **controlled batches** (about 5–8 deals per parallel batch), not one long sequential chain and not an unbounded fan-out. If a call fails for a deal, drop that deal from that analysis only and record the reduced n.

3. **Framework deep-dives** — `opportunity_framework_summary` with `framework: "MEDDPIC"`; also BANT and SPICED if requested. Record **when** each score was captured (stage at capture) — see the stage-capture bias rule in Step 3b.
4. **Deal narratives** — `get_opportunity_notes_summary` for each sampled deal; for lost deals also `get_opportunity_notes`. When a lost deal's notes name a competitor, call `get_battlecard` for that competitor. Notes reveal pricing objections, competitor names, procurement blockers and stated loss reasons; won-deal notes reveal champion language, urgency triggers and proof points.
5. **Deal details** — `get_opportunity`: health at close, owner, account linkage, stage history, current stage.
6. **Activity sequences** — `get_opportunity_activities`: volume by type, cadence between touches, last activity type before outcome, momentum. Feeds Slide 8 and Step 3e.
7. **Revenue Signal Layer** — `get_opportunity_signals` (same sample only; it is per-deal and access-guarded). Win-probability movement and the flagged first constraint. If unauthorized or empty for a deal, drop that deal from the signal analysis only and note the reduced n on Slide 5.
8. **Stakeholder coverage** — `opportunity_stakeholder_intelligence` (same sample only). Engaged-stakeholder counts and roles, to state a measured multi-threading figure instead of inferring it from note text.

### Context pulls (parallel with the above)

9. **Forecast accuracy** — `forecast_confidence`.
10. **ARR context** — `arr_growth_analytics` with `include_trends: true`, `include_benchmarks: true`.
11. **Account health** — `account_intelligence_summary`.
12. **Account engagement and drag** — `activity_gaps`; `deal_drag_dashboard` filtered to closed-lost; `deal_drag_summary` for the sampled lost deals. "Stalled-then-lost" (failure to sustain urgency) is a different pattern from "lost in active evaluation" (lost on merit).
13. **Canonical win rate by deal size** — `unified_forecast_summary`, `kpis.win_rate.by_deal_size`. On a processing envelope, poll `get_job` to terminal and re-call with identical arguments. These bands are auto-detected from p25/p50/p75 of the org's trailing-12-month closed-won history. Use them as the canonical band definition for Step 3a and as a cross-check against your cohort; if your cohort's band rates diverge sharply, note that the windows differ. **If the band definition remains unavailable, stop and state the missing source; do not substitute hard-coded brackets.**
14. **Rep coaching grounding** (optional, permission-gated) — `coaching_diagnostic` per rep represented in the sample. If unauthorized for a rep or the team, skip it and keep pattern-level language.

### Handling missing data

- **Small denominators.** If either outcome pool has fewer than 10 deals, show counts ("3 of 7"), not percentages alone, and label findings "early observations". Below 5 per side, state that patterns cannot be distinguished from noise.
- Framework errors for some deals → skip those deals in that comparison and show the reduced n.
- Empty forecast-confidence history → drop the forecast-accuracy content and note "Forecast history unavailable."
- `get_opportunity_signals` or `coaching_diagnostic` unauthorized → drop that enhancement only, note it, keep the deck.
- A null, empty or access-denied field is **unavailable**, never zero, and never a reason (see Step 3d).

## Step 3: Analyse and synthesise

Write internal findings before building slides. Every number carries its n.

### 3a: Outcome rates — define every rate

Define each rate where it is first shown:

- **Win rate** = won ÷ (won + lost) within the cohort definition. State whether no-decision/withdrawn outcomes are excluded.
- **Win rate by deal-size band** — use the org-adaptive bands from `kpis.win_rate.by_deal_size` (`rate`, `won`, `total`, `label` per band). Show `won`/`total` beside each rate. A blended win rate usually hides a weak band; this is often the single most useful cut.
- **Win rate by rep** — only with n per rep, only where the audience is authorized, and never ranked on tiny denominators.
- **Stage reached before loss** — where did lost deals stop?
- **Cycle time** — median days from create to close, wins vs losses.

**Segment when confounded.** If deal size, motion (new business vs expansion vs renewal), region, customer tenure or stage history differ materially between the won and lost pools, the blended comparison can mislead. Split by that dimension and compare like with like; if a segment is too small to compare, say so.

### 3b: Framework score comparison

For each framework element (MEDDPIC, BANT, SPICED):

- Average on won deals vs average on lost deals, with n for each side.
- The gap between them.
- Rank elements by gap — these are the **elements most strongly associated with outcome in this cohort**, not predictors.

**Stage-capture bias.** Lost deals often die early, when frameworks are naturally less complete; won deals are scored at late stages. A large gap can reflect when the score was captured rather than what drove the outcome. Where possible, compare deals at the same stage (for example, only deals that reached the same stage, or scores captured at that stage). Otherwise flag the bias next to the comparison.

**Trajectory layer** (`get_opportunity_signals`): compare win-probability movement over the lifecycle, and when the flagged first constraint appeared relative to close. A loss with a constraint flagged 6+ weeks out is a different pattern from one flagged in the final week. This separates "what was true at close" from "how the deal got there". Show how many deals had signal data.

### 3c: Risk factor patterns

From `risk_heatmap`:

- Risk factors most frequent on lost deals, and on won deals (some factors are not associated with loss at all) — with counts.
- Median `healthScore` at close for wins vs losses (higher = healthier). Note that health at close is partly a consequence of the outcome, not only an input.

### 3d: Qualitative notes — code themes, count deals

Code each sampled deal's notes against a consistent theme list, then count deals per theme ("Procurement resistance — 4 of 7 sampled losses").

**Lost-deal themes**: competitor mentions and concessions; objection types (pricing, integration footprint, procurement, timing); stall patterns (a stated next step with no follow-through activity); loss reasons.

**Loss reason sourcing** — label each lost deal's reason as one of:

- **Stated** — an explicit loss-reason field or note says so;
- **Inferred from notes** — paraphrased from note content, flagged as inferred;
- **Unknown** — the field is empty and the notes do not say. **Never infer a loss reason from an empty field.** Report the unknown count.

**Won-deal themes**: champion language ("confirmed exec approval"), proof points that closed objections, urgency triggers, multi-threading.

**Measured multi-threading** (`opportunity_stakeholder_intelligence`): replace inferred multi-threading with the measured figure, e.g. "Won deals averaged 4.6 engaged stakeholders (n=7) vs 1.8 on losses (n=6)."

**Battlecard enrichment** (`get_battlecard`): for competitors named in lost-deal notes, add the battlecard's structured differentiators, e.g. "Competitor X mentioned in 3 of 5 sampled losses — battlecard flags [differentiator] as the counter; confirm reps used it."

Paraphrase notes; do not quote sensitive verbatim notes when a theme is enough. Synthesise 2–3 qualitative observations to pair with the quantitative findings.

### 3e: Activity and engagement patterns (deal level)

From `get_opportunity_activities`, for sampled won vs lost deals (state n):

- **Volume** by type — e.g. "Won deals averaged 8.2 activities (2.3 calls, 3.1 emails, 2.1 meetings, n=7) vs 4.1 on losses (n=6)."
- **Cadence** — average days between touches.
- **Last activity before outcome** — share with a call or meeting in the final 7 days, as counts.
- **Momentum** — clustered near close vs flat or declining.

Absent logged activity is not proof of no engagement — reps may not log everything. Say "logged activity".

**Stalled-loss vs active-loss segmentation:**

- **Active-loss** — high logged activity and/or recent engagement (low staleness): competitive or merit-based loss during active evaluation.
- **Stalled-loss** — low activity and/or long gaps before the loss (high staleness): failure to sustain momentum.

Use `deal_drag_dashboard` waste scores or activity recency as the criteria and state the threshold. Where `deal_drag_summary` names a top qualification gap, a stalled-loss with a named gap (e.g. missing Economic Buyer) is a coaching target; an active-loss with clean qualification but high drag points to competitive or pricing pressure.

### 3f: Recommendations as validation tests

Generate 5–7 recommendations. Each one is a **measurable validation test**, not a proven fix:

- **Change** — the process change to trial (e.g. "Add a Champion validation checkpoint at Stage 3").
- **Evidence** — the association that motivates it, with n.
- **Test** — cohort, window and metric (e.g. "Apply to all new Stage 3 opportunities next quarter; compare Stage 3→close conversion with the prior two quarters").
- **Success threshold** — what result would confirm it, and the minimum n needed to judge.
- **Loss type** — For stalled-losses (urgency, cadence, momentum), For active-losses (differentiation, qualification depth, positioning), or For all losses.

Order by expected impact. Frame as process, not blame ("Add a Champion checkpoint", not "Reps aren't finding champions"). Where `coaching_diagnostic` is available and authorized for a rep, ground that rep's line in the flagged layer; otherwise keep it at pattern level and route individual coaching to `rep-coaching-report`.

### 3g: Headline

One sentence, in association language, with n:

- "Strong Champion scores are the clearest pattern separating wins from losses (avg 82% vs 31%, n=7/6) — worth validating with a Stage 3 checkpoint."
- "Paper Process was undefined on 7 of 9 sampled losses."
- "Won deals logged roughly 3× more touches in the final 30 days (n=7 vs 6)."

## Step 4: Build the deck

Build with PptxGenJS following the `pptx` skill: read its SKILL.md and its `pptxgenjs.md` reference before writing code.

### Design system

Use the **Cherry Bold** palette — this is an analytical/diagnostic deck, not a boardroom update; the bold red gives urgency and distinguishes it from operational decks.

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
| Subtle border / unavailable | Slate | `64748B` |
| Muted text | Slate | `94A3B8` |

**Typography**: Georgia headers (36–44pt), Calibri body (14–16pt).
**Layout**: 16:9 widescreen, 0.5" minimum margins. Dark title/close slides, light content slides. Demo label on every slide if it applies. Every percentage on every slide carries its n (e.g. "71% (5/7)").

### Slide structure (11 slides)

#### Slide 1: Title
- Cherry background. Company name, "Win/Loss Pattern Analysis", period covered, date. Large Georgia title in white, Calibri subtitle in off-white.

#### Slide 2: Executive summary
- Cherry background. The Step 3g headline as a large callout (28–32pt, white), then 3 key findings (16–18pt, off-white), each with n.
- Answers: "What's the one thing to take away — and how confident should we be?"

#### Slide 3: Win/loss summary
- Sources: Step 3a; health at close from `get_opportunity`.
- Four stat cards: win rate (with won/total), won count, lost count, median deal size (won vs lost). Bar chart of win rate by org-adaptive deal-size band with `won/total` labels. Emerald for wins, cherry for losses.
- Cohort line beneath: window, stage definitions, exclusions by reason, and the truncation note if the cohort is incomplete.
- Optional: median health score at close, won vs lost, with the caveat that health at close partly reflects the outcome.

#### Slide 4: Framework score comparison (MEDDPIC)
- Source: Step 3b.
- Horizontal grouped bar chart, one pair per MEDDPIC element; emerald won, cherry lost; n in the legend.
- Callout: the element with the largest gap, phrased as an association, plus the stage-capture bias note where it applies.
- Limited data → table: element, win avg, loss avg, gap, n.

#### Slide 5: Patterns associated with wins
- Sources: ranked elements from Step 3b, trajectory data from `get_opportunity_signals`.
- Top 5 elements by gap, each as a card: element name; win avg → loss avg with gap; **n for each side**; one-line interpretation in association language ("Wins in this cohort had markedly stronger Champion scores (n=7 vs 6)").
- Navy numbered circles (1–5). Colour the gap emerald when it favours wins, cherry when a low score is associated with loss.
- Trajectory strip where signal data exists (state how many deals): e.g. "On 4 of 6 lost deals with signal data, a first constraint was flagged a median 5 weeks before close."
- Footer: "Associations in this cohort — not validated predictors. See validation tests on Slide 10."

#### Slide 6: BANT and SPICED comparison
- Source: Step 3b. Two columns: BANT (Budget, Authority, Need, Timeline) and SPICED (Situation, Pain, Impact, Critical Event, Decision), win vs loss averages with n, as mini-bars or a compact table.
- Score colours: emerald ≥ 70%, amber 40–69%, red < 40%, slate unavailable.
- Only one framework → full width. Neither → skip the slide.

#### Slide 7: What the field is saying (qualitative themes)
- Sources: Step 3d coding, `opportunity_stakeholder_intelligence`, `get_battlecard`.
- Two columns: "Why we win" (emerald left-border cards) and "Why we lose" (cherry left-border cards), 3–4 cards each. Each card: theme name, **deal count** ("4 of 7 sampled losses"), 1–2 paraphrased lines of evidence.
- Stat line: measured engaged stakeholders, won vs lost, with n.
- Loss-reason sourcing line: "{s} stated, {i} inferred from notes, {u} unknown."
- Competitive intelligence callout if competitors appear in lost-deal notes, with mention count and battlecard counters.
- Sparse notes → single column and a limited-sample note.

#### Slide 8: Activity and engagement patterns
- Sources: Step 3e, `activity_gaps`, `deal_drag_dashboard`, `deal_drag_summary`.
- Three sections: logged activity volume by type (won vs lost, n); cadence (average days between touches); final activity type in the last 7 days (counts).
- Key insight in association language: "Won deals in this cohort logged a touch roughly every 5 days; lost deals showed ~13-day gaps (n=7 vs 6). Tighter cadence is associated with wins here — validate before treating it as a rule."
- Callout: "Of {X} lost deals, {Y} active-losses and {Z} stalled-losses (threshold: {criterion})." Add the most common named qualification gap on stalled-losses where `deal_drag_summary` provides it.

#### Slide 9: Common loss patterns
- Sources: Steps 3c, 3d, 3e and `deal_drag_summary`.
- Cards with a cherry left border: pattern name; loss-type badge ("Active loss" or "Stalled loss"); frequency as a count ("5 of 9 lost deals"); one line of evidence blending quantitative and qualitative. Top 5–6 patterns, active and stalled grouped separately.
- A named top qualification gap shared across several stalled-losses gets its own card.
- Include an "Unknown reason" card if the unknown count is material.

#### Slide 10: Recommendations as validation tests
- Source: Step 3f.
- 5–7 numbered items (navy circles): bold change headline; evidence with n; test (cohort, window, metric); success threshold; loss-type tag.
- Order by expected impact. Process framing, not blame.

#### Slide 11: Close — cohort, definitions and limits
- Cherry background. Company name, "Evidence to improve win rates", date, "Powered by Summit53".
- Lower block (off-white): cohort definition, rate definitions, exclusions, sample selection rule, truncation status, unavailable sources (summarised), stage-capture bias note, the demo label if it applies, and "Associations, not validated predictors."

### Chart generation

Prefer native PptxGenJS charts (BAR, DOUGHNUT, PIE) so they stay editable. Match colours to the palette; use the `pptxgenjs.md` styling guidance (custom colours, clean backgrounds, muted axis labels, subtle grids). For Slide 4 use two series (Won, Lost) with `barDir: 'col'` in emerald and cherry. Start value axes at zero; no truncated axes that exaggerate gaps.

## Step 5: Generate the file

Write one Node.js PptxGenJS script that:

1. Embeds all pulled and calculated data directly (no external data files).
2. Uses helpers for stat cards, pattern cards and comparison bars.
3. Uses factory functions for shadows and option objects (never reuse option objects across `addShape` / `addText` calls).
4. Builds every slide above.
5. Handles missing data, empty arrays, nulls and small samples — renders "unavailable" rather than `0`, and counts alongside percentages.
6. Saves to the session's outputs directory as `Win-Loss-Analysis-[CompanyName]-[Date].pptx`.

## Step 6: Render, QA and deliver

1. Render **every** slide to an image using the `pptx` skill's render/thumbnail flow (or `soffice --headless --convert-to pdf` then `pdftoppm -jpeg -r 150`).
2. Inspect each slide at full size: overlap, clipping, wrapping, contrast, misleading scales, placeholder text, small-sample overstatement.
3. Check every number against the source payloads, and every percentage for its n.
4. Fix and re-render; do not declare success before at least one fix-and-verify cycle.
5. Return **one clickable link** to the PPTX, followed by a short note on cohort scope, exclusions, truncation and unavailable sources.

## Tips for great win/loss analysis

- **Let the data tell the story, at the size it is.** If the sample is small, say so on the slide.
- **Compare, don't just describe.** "Champion scores average 72% on wins" is weak. "Champion scores average 72% on wins vs 28% on losses (n=9/8) — the largest gap in this cohort" is useful — and still an association.
- **Make recommendations testable.** "Improve qualification" is useless. "Add a Champion validation question to Stage 2 exit criteria and compare Stage 2→3 conversion next quarter" is implementable and checkable.
- **Acknowledge limitations.** Small samples, missing frameworks, stage-capture bias and unlogged activity are fine — the audience needs them to calibrate.
- **Frame losses as learning.** Curiosity, not blame; process improvement, not finger-pointing.

## Verification checklist

- [ ] Preflight checklist complete; `scoped_org_id` matched on returned data
- [ ] Cohort defined; complete via bounded windows, or truncation disclosed on Slides 3 and 11
- [ ] Open, duplicate, deleted, incomparable and fixture records excluded and counted
- [ ] Every rate defined; every percentage shows its n; small denominators shown as counts
- [ ] Segmented where size, motion, region, tenure or stage history confound
- [ ] Themes show deal counts; loss reasons labelled stated / inferred / unknown; none inferred from empty fields
- [ ] Stage-capture bias flagged on framework comparisons
- [ ] No "predictor", "predicts" or "money slide" language; recommendations are validation tests
- [ ] Deal-size bands from `unified_forecast_summary`, or the missing source stated and the run stopped
- [ ] Cherry Bold palette; demo label applied if fixtures could not be excluded
- [ ] Every slide rendered and inspected; one link returned
