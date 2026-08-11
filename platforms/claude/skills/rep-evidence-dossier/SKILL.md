---
name: "rep-evidence-dossier"
description: "Assemble a neutral, defensible Summit53 evidence dossier for a promotion, PIP, calibration, talent review, or documented performance concern. Screen structural confounders and evidentiary depth before presenting performance evidence, and never render an employment recommendation. Use for promotion cases, HR documentation requests, calibration preparation, or questions such as 'what have we done to help this rep?'. Do not use for a routine 1:1."
version: "2.1.0"
baselined: "2026-08-08"
status: "active"
---

# Rep Evidence Dossier

Serves **RL7 — defending a promotion** and **RL8 — putting someone on a PIP**.

## The moments this serves

**RL7 — calibration.** Manager to VP/CRO, peer managers in the room. The dreaded
question comes from a peer whose candidate just got passed over: *"Why them and not
[other rep]?"* Today: a case assembled from memory and last quarter's numbers, in a room
where everyone is doing the same and the loudest advocate wins.

**RL8 — the PIP.** Manager, HR, sometimes legal. The dreaded question is not about the
rep: *"What did you do to help them before this?"* A thin answer makes the PIP
indefensible and ends the **manager's** career, not the rep's. Today: reconstructing
months of coaching history from calendar invites and memory.

## What changed in this rebuild

Rebuild of `rep-coaching-report`, which aimed at the 1:1 — a ritual, not a hot seat.
Nobody's credibility is on the line in their own coaching session. The tools underneath
were right; the target was wrong.

Also fixed, per Tier 0:

- **`complete_coaching_session` removed.** It exists on neither server. The entire
  close-the-loop half of the old skill had no backing tool and would have failed at the
  moment a manager tried to log a session.
- **`coaching_diagnostic` and `coaching_agenda` are now read-stored**, not get-or-
  generate. The old skill was written against generate behaviour and degraded silently
  into empty sections. This skill handles the no-stored-record case explicitly.

---

## The constraint that governs everything

**This artifact carries employment-law exposure.** In New Zealand and Australia a
personal grievance claim will test exactly this documentation — whether the decision was
one a fair and reasonable employer could reach, and whether a fair process preceded it.

Three rules follow, and none are negotiable:

1. **The dossier renders no recommendation.** It does not conclude the rep should be
   promoted, managed out, or retained. It assembles evidence and hands the decision to
   the human accountable for it. A tool that recommends a PIP has, in a hearing, made
   the decision — and the manager cannot then claim to have exercised judgement.
2. **Structural confounders appear before performance evidence.** Document order, not
   tone. See `references/structural-confounders.md`.
3. **Absence is reported, never omitted.** A missing record is a finding. An empty
   section is a defect.

Getting this right is a credibility asset, not just risk management. It is also the
honest position: the platform can assemble evidence far better than it can adjudicate a
person's career.

---

## Step 0 — References

Read all three from this skill's directory before any calls:

- `references/structural-confounders.md` — **the six screens. Run these first.**
- `references/delta-attribution.md` — for any rep metric presented as a movement.
- `references/async-envelopes.md` — processing envelopes read as data produce blank
  sections, which in this artifact means missing evidence in an HR meeting.

## Step 1 — Establish purpose and rep

Ask which rep, and **ask what decision this supports**: promotion, PIP, calibration, or
general documentation. The purpose changes what the dossier emphasises, and asking it on
the record is itself good process.

Resolve the rep ID from `coaching_intervention_plan` (returns the full roster with
`user_id` and `name`) rather than guessing from opportunity ownership.

If the user declines to name a purpose, default to **calibration** — the least
prejudicial framing — and note the default in the dossier header.

## Step 2 — Run the confounder screens FIRST

Do not pull performance data yet. Run the six screens in
`references/structural-confounders.md`:

| Screen | Tool |
|---|---|
| 1. Flag base rate | `coaching_intervention_plan` |
| 2. Territory / segment | `segment_performance_summary`, `search_opportunities` |
| 3. Ramp status + survivorship | `ramp_cohort` |
| 4. Role–motion fit | `hunter_farmer_mix` |
| 5. Evidentiary depth | `coaching_development`, `coaching_meeting_analytics`, `coaching_agenda` |
| 6. Ledger scope | `list_interventions`, `get_intervention_outcome` |

`rep_coaching_context` bundles diagnostic + development + meeting analytics + agenda in
one call and is the efficient way to run Screen 5. The granular tools remain
authoritative — if the bundle and a granular call disagree, use the granular value and
note the discrepancy.

### The depth gate stops the skill

If Screen 5 returns zero across all four depth signals, **stop**. Produce the
record-state finding and no performance evidence:

> No documented coaching record exists for this rep in Summit53: 0 weeks of stored
> diagnostic history, 0 development goals, 0 meetings analysed, 0 rep-scoped
> interventions. This dossier cannot support a performance decision. It can only report
> that the documentary record required to defend one has not been created.
>
> Coaching delivered outside the platform will not appear here. If it occurred, it needs
> to be documented before this decision proceeds.

That is a complete and useful deliverable. A manager who learns this before the HR
meeting can still act on it. Padding it out with pipeline numbers to make it look
substantial would actively mislead — it would suggest evidence exists where it does not.

Live check on Staging: rep 94 returned 1 week of history, 0 goals, 0 meetings. Rep 98's
agenda returned `status: "not_generated"`. **This gate will trip on real data.** It is
not a defensive edge case.

## Step 3 — Performance evidence

Only if the depth gate permits. Every item below is a **finding**, never a verdict.

**Attainment and pipeline**
- `forecast_confidence` rep-filtered, and unfiltered for the team comparator
- `search_opportunities` rep-filtered — book composition
- `pipeline_risk_summary` rep-filtered

Compare against the **rep's segment**, per Screen 2. Where a team comparator is used,
state that it spans segments and is therefore not like-for-like.

**Execution behaviour**
- `activity_gaps` (`days: 30`, `owner_ids: [rep]`)
- `deal_drag_dashboard` / `deal_drag_summary` rep-filtered
- `team_action_plan` (`user_id: rep`) — action completion

**Qualification discipline**
- `opportunity_framework_summary` on up to 8 of the rep's deals
- `list_methodology_playbooks` — the org's own definition of "what good looks like".
  Grounding the standard in the org's published playbook rather than a generic one
  matters here: a rep cannot be held to a standard that was never published to them, and
  that argument lands hard in a grievance process.

**Observed meeting behaviour**
- `coaching_meeting_analytics` (`weeks: 13`) — talk ratio, question rate, monologue
  length, interruptions

This is the most defensible category in the dossier because it is **observed behaviour
rather than opinion**. Where `total_meetings: 0` (live on Staging), say so — the
category is unavailable, not neutral.

**Development trajectory**
- `coaching_development` — 13-week diagnostic history, 26-week focus-metric trend,
  development goals with progress

Where history exists, this is the evidence trail. Render it as a timeline with dates.
Where `focus_metric_trend` is populated, present it per
`references/delta-attribution.md` — movement with a stated comparison window, not a bare
current value.

## Step 4 — Assemble

Markdown primary, saved as `Rep-Evidence-Dossier-{RepName}-{YYYY-MM-DD}.md`. Offer a
DOCX render if the user is taking it into an HR meeting — read the `docx` skill for
mechanics. Do **not** default to PPTX: slides invite summary bullets, and a summary
bullet in a grievance file is a liability. This artifact wants prose, dates, and sources.

```markdown
# Rep Evidence Dossier — {Rep Name}
Prepared {date} · Purpose: {promotion | PIP | calibration | documentation}
Prepared by {user} from Summit53 records as at {as_of}

> **This dossier renders no recommendation.** It assembles the documentary record and
> the structural factors bearing on it. The decision, and the reasoning for it, belong
> to the manager and are not produced here.

## 1. Evidentiary depth
{Screen 5 table + banner if the gate trips. Always first.}

## 2. Structural factors
{Screens 2, 3, 4 — each: what was checked, what was found, what it means for the weight
the evidence below can carry. Include "not assessed" entries with reasons.}

## 3. Signal reliability
{Screens 1, 6 — base rates, composite-score ties, ledger scope limits.}

## 4. Documented coaching record
{Timeline with dates from coaching_development. Development goals and progress.
Interventions assigned to the rep, labelled as execution accountability, not coaching.
Where the record is thin, say how thin.}

## 5. Observed behaviour
{coaching_meeting_analytics. Or explicit unavailability.}

## 6. Performance evidence
{Attainment vs segment. Pipeline. Execution. Qualification vs the org's own playbook.
Each with its comparator named.}

## 7. What this dossier cannot establish
{Standing limits — see below. Never omit.}

---
Sources: {every tool called, with as-of timestamps and any async notes verbatim}
```

### Section 7 — standing limits

Include every one that applies. These are not hedges; they are the boundary of what the
record supports, and a decision-maker needs them.

- **Coaching outside the platform is invisible.** The record reflects what was stored in
  Summit53, not what occurred.
- **Ramp benchmarks are survivorship-biased.** Cover only reps currently in their ramp
  window; exclude everyone who left. Read as best case. Attrition is not tracked.
- **The Intervention Ledger is not rep-scoped.** Its entity types are account,
  opportunity, source and lead. Records shown are interventions *assigned to* this rep,
  not coaching *delivered to* them.
- **Intervention outcomes are correlational.** The ledger reports
  `causal_claim_supported: false`. Movement within an outcome window is association.
- **Segment comparisons rest on territory resolution**, not an explicit segment field.
- **Attainment is not adjusted for account quality or inherited pipeline.** No tool
  measures the book a rep was given versus the book they built.
- **Meeting analytics cover recorded meetings only.** Unrecorded coaching does not
  appear.
- **No recommendation is rendered, by design.**

---

## Step 5 — Language rules

Enforced by review before delivery. Search the draft for each.

**Banned — conclusions the dossier is not entitled to draw:**
`underperformer`, `not meeting the bar`, `should be`, `recommend`, `poor performer`,
`failing`, `unable to`, `lacks`, `caused`, `because of their`, `due to poor`.

**Required substitutions:**

| Instead of | Write |
|---|---|
| "Rep is underperforming" | "Attainment is X% against a segment benchmark of Y%" |
| "Coaching didn't work" | "Focus metric moved from X to Y over the window; the record does not establish why" |
| "Rep lacks discovery skills" | "Discovery score averaged X across N deals, against the org playbook standard of Y" |
| "Needs a PIP" | *(nothing — the dossier does not say this)* |
| "Intervention worked" | "Metric moved X → Y in the outcome window; ledger label 'worked'; correlational" |

Every performance statement is a **measurement with a comparator and a window**. If a
sentence cannot be written that way, the underlying data does not support the sentence.

Naming a comparison rep is permitted **only** in calibration mode, only using the same
metrics on the same window and same segment, and only with the segment caveat attached.
Cross-segment rep comparison is not evidence and must not appear.

---

## Step 6 — Verify

Content checks. A dossier that generates cleanly and says nothing has failed, and in this
artifact a thin section is worse than no section.

1. **Order.** Is evidentiary depth section 1 and structural factors section 2, above all
   performance content? If not, the dossier fails its core constraint.
2. **Depth gate.** If depth signals were zero, did the skill stop rather than proceed?
3. **No recommendation.** Search for the banned list. Zero hits required.
4. **Comparators.** Does every performance number carry a named comparator and window?
5. **Absences rendered.** Is every unavailable source stated as unavailable, rather than
   silently missing? Cross-check the tool list against sections rendered.
6. **Causal language.** Search "caused", "because", "led to", "resulted in", "proves",
   "shows that they". Rewrite each.
7. **Ramp caveat.** If any ramp figure appears, is the survivorship caveat adjacent —
   same section, not a footnote?
8. **Ledger labelling.** Are intervention records labelled as assigned-to rather than
   coaching-delivered?
9. **Empty-vs-zero.** Is any `0` in the artifact actually a `null`, `[]`, or
   `not_generated` from the source? Live traps: `total_meetings: 0`,
   `development_goals: []`, `coaching_agenda.status: "not_generated"`.

Fail any of 1, 2, 3 and the dossier must not be delivered.

## Step 7 — Deliver

Present the file and say plainly, in chat, what the dossier does and does not do — that
it renders no recommendation, and that the depth finding (if it tripped) is the most
important thing in it.

If the depth gate tripped, add one sentence on what would close the gap: which records
need creating in the Coaching dashboard, and that they need to accrue over time rather
than be backfilled. Backfilling a coaching record ahead of a PIP is precisely what a
grievance process is designed to detect, and it should not be suggested.

## Tools

| Tool | Role |
|---|---|
| `coaching_intervention_plan` | Roster, rep IDs, flag base rate (Screen 1) |
| `segment_performance_summary` | Territory comparator (Screen 2) |
| `ramp_cohort` | Ramp status + survivorship disclosure (Screen 3) |
| `hunter_farmer_mix` | Role–motion fit (Screen 4) |
| `rep_coaching_context` | Bundled depth probe (Screen 5) |
| `coaching_development` | Diagnostic history, trend, goals — **authoritative** |
| `coaching_meeting_analytics` | Observed behaviour — **authoritative** |
| `coaching_diagnostic` | Stored diagnostic (read-stored; handle empty) |
| `coaching_agenda` | Stored agenda (handle `status: "not_generated"`) |
| `list_interventions` / `get_intervention_outcome` | Assigned interventions only (Screen 6) |
| `forecast_confidence`, `search_opportunities`, `pipeline_risk_summary` | Attainment and pipeline |
| `activity_gaps`, `deal_drag_dashboard`, `deal_drag_summary`, `team_action_plan` | Execution behaviour |
| `opportunity_framework_summary`, `list_methodology_playbooks` | Qualification vs the org's own standard |

**Removed:** `complete_coaching_session` — does not exist on Staging or Prod.
