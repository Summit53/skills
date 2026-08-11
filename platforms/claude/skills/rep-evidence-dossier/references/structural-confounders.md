# Structural Confounders — Screening Protocol

**Version 2.0.0 · baselined 2026-08-08 (post-fix) against Summit53_Staging.**
Screens 1, 1b and the verified-zero check are now server-supported — read the
fields rather than hand-rolling them.
Reference for `rep-evidence-dossier`. Read before assembling any dossier.

---

## Why confounders come first

A rep behind quota because of territory assignment is not a performance case. A rep
measured against a survivorship-biased ramp benchmark is not a performance case. A rep
flagged by a system that flags 95% of the team is not a performance case.

In a New Zealand or Australian personal grievance claim, the employer must show the
decision was one a fair and reasonable employer could have reached, and that a fair
process preceded it. A dossier that leads with underperformance and mentions territory
in a footnote — or not at all — is the document that loses that argument. Not because the
conclusion was necessarily wrong, but because the process visibly failed to test it.

So the screen runs **first**, and its results are rendered **above** any performance
evidence in the artifact. This is a document-ordering rule, not a tone preference. If the
confounder section sits below the numbers, the dossier has failed regardless of content.

---

## Screen 1 — Base rate of the flag

**Source:** `coaching_intervention_plan` → `coaching_flag_quality`, `ordering`.

As of the 8 Aug 2026 fix the server computes this for you. **Do not hand-roll it.**

```json
"coaching_flag_quality": {"classification": "non_discriminating",
  "roster_reps": 20, "evaluated_reps": 19, "flagged_reps": 18, "flag_rate": 0.9474,
  "diagnostic_coverage_rate": 0.95, "minimum_sample": 4,
  "non_discriminating_threshold": 0.75,
  "warning": "The coaching flag applies to at least 75% of evaluated reps and must not
              be used as an ordinal performance ranking."},
"ordering": {"ordinal_ranking": false, "basis": "cohort_then_name",
             "note": "Tied composite scores are not broken into artificial ranks."}
```

Rules:

1. If `classification` is `non_discriminating`, **the flag is not evidence.** Quote
   `warning` verbatim and do not cite the flag against this rep.
2. **Never render an ordinal rank.** `ordering.ordinal_ranking: false` and
   `metadata.ordinal_ranking: false` prohibit it. No "coaching priority #N of M", ever —
   the ties that made it unsound (three reps at 0.8558, three at 0.6100) are still there
   and the server now refuses to break them.
3. Note `roster_reps: 20` vs `evaluated_reps: 19` — one rep has no diagnostic at all.
   If that rep is the dossier subject, Screen 5 governs and there is no flag to discuss.

Dossier line when suppressed:

> The coaching flag applies to 18 of 19 evaluated reps (94.7%), which the system itself
> classifies as non-discriminating. It does not distinguish this rep from the team and is
> not presented as evidence.

### Per-rep evidence sufficiency — the new gate

Each rep in `reps[]` now carries:

```json
"evidence_sufficiency": {"window_weeks": 4, "observed_weeks": 1, "flagged_weeks": 1,
  "persistent_needs_coaching": false, "minimum_observations_for_persistence": 2}
```

**`persistent_needs_coaching` is the only flag-derived signal admissible in this
dossier.** A single flagged week is a weekly-cadence artifact, not a pattern. Live, every
rep on the roster returns `false` — one observed week against a minimum of two.

If `persistent_needs_coaching` is `false`, state it plainly:

> The coaching flag has been observed for 1 week against a 4-week window; the system
> requires 2 observations to treat it as persistent and does not. There is no established
> pattern.

---

## Screen 1b — What "the benchmark" actually is

**Source:** `coaching_diagnostic` → `benchmark_context` (also echoed per-rep in
`coaching_intervention_plan`).

As of the 8 Aug 2026 fix the server labels this itself:

```json
"benchmark_context": {"source": "team_p75", "role": "aspirational_team_benchmark",
  "percentile": 75, "peer_average": false, "peer_count": 19,
  "warning": "Below team P75 does not by itself mean below-average performance."}
```

**Quote `warning` verbatim wherever a benchmark comparison appears.** `role:
"aspirational_team_benchmark"` and `peer_average: false` are the operative fields —
roughly 75% of any team sits below a P75 bar by construction, so "below benchmark" is
the normal state, not a deficiency finding.

Remaining checks the server does not do for you:

1. **`peer_count` varies by metric.** Live, `framework_completeness` benchmarks use
   n=19 but `discovery_score` uses **n=5**, against a `min_peer_count` of 4. A percentile
   over five peers is unstable; say so where it is the basis of a comparison.
2. **`role: "reference"` with `source: null`** appears for reps with no diagnosed layer
   (live: Maya Williams). There is no benchmark — do not substitute the team one.
3. Prefer median or segment-median for a performance argument. P75 can establish
   below-top-quartile, never below-average. Different claims.

### Verified zero vs unverified — `_evidence`

As of the 8 Aug 2026 fix, `results_scores` distinguishes a real zero from missing data:

```json
"results_scores": {"quota_attainment": null, ...,
  "_evidence": {"quota_attainment": {"status": "legacy_unverified",
                "verified": false, "fresh": false, "refreshed_at": null}}}
```

`quota_attainment` previously returned **0.00** — which this dossier flagged as
internally inconsistent with three closed-won deals. It now returns `null` with
`status: "legacy_unverified"`. The earlier reading was an artifact, and the dossier was
right not to carry it into a decision.

**Rule:** check `_evidence[metric].verified` before citing any `results_scores` value.
Where `verified: false`, report the metric as **not established**, naming the status.
Never render `null` as zero, and never treat an unverified metric as a finding.

Note `benchmarks_used.quota_attainment` still returns `0.95` even when the rep's own
value is `null`. A benchmark without a measurement is not a gap. Do not compute one.

### Check the size of the gap before calling it a gap

Live for rep 98: `focus_metric_current: 0.5512` against
`focus_metric_benchmark: 0.5737` — `focus_metric_gap_pct: 0.0392`. A **3.9%** shortfall
against a top-quartile bar, and the rep is nonetheless flagged `needs_coaching: true`
with a diagnosed layer of `knowledge`.

A 3.9% gap to P75 is not a performance case. It is close to the bar. The flag exists to
route weekly coaching attention, not to support an employment decision, and it does not
become one by being copied into a document.

Render the gap as a **magnitude**, always:

> Framework completeness: 0.551 against a team-P75 benchmark of 0.574 — a gap of 3.9%.
> The rep sits just below a top-quartile bar. This does not evidence underperformance.

Where the gap is under 10%, add explicitly that it does not support a performance
conclusion. Where the diagnostic's selected `focus_metric` shows a small gap while a
different metric in `results_scores` shows a large one (live: `quota_attainment: 0.0`
against a 0.95 benchmark), **report both** and note that the system selected the focus
metric on improvement *leverage* — speed and tractability — not on severity. The
diagnostic is a coaching-prioritisation tool. It is not ranking how badly someone is
doing, and reading it that way inverts its meaning.

Also check `skills_scores.low_scoring_components`. Live it returned `[]` — no skills
component was flagged low. An empty array is a **positive** finding and belongs in the
dossier. Omitting it while retaining the negative signals is selective presentation.

---

## Screen 2 — Territory and segment assignment

**Sources:** `segment_performance_summary`, `search_opportunities` (rep-filtered),
`account_intelligence_summary`.

Segment-level performance differences are structural. They attach to the patch, not the
person.

Live on Staging: Enterprise win rate **44.4%** vs Commercial **68.4%**. A rep working
Enterprise sits 24 points below a Commercial peer before any individual difference is
considered. Comparing the two on raw win rate is comparing territories.

Procedure:

1. Determine which segment(s) the rep's book sits in.
2. Pull that segment's `win_rate`, `sales_cycle_days`, `first_contract_acv`,
   `pipeline_coverage`.
3. Compare the rep against **their own segment**, not the blended team number.
4. If the rep's segment underperforms the blended rollup, state the gap explicitly and
   quantify how much of the rep's shortfall the segment difference alone accounts for.

**Segment basis caveat.** `segment_source` reports
`no_explicit_segment_field_configured: true` — segments are resolved from segment
*territories*, so "Enterprise" means the Enterprise territory rather than an account-size
classification. State this. A reader assuming deal-size segmentation draws a wrong
conclusion about what the comparison controls for.

If segment membership cannot be resolved, say the comparison could not be made. Do not
fall back to the blended average and present it as like-for-like.

---

## Screen 3 — Ramp status and the survivorship problem

**Source:** `ramp_cohort`.

Two separate issues, both disqualifying if ignored.

### 3a — Is the rep still ramping?

If the rep appears in `reps[]` they are inside their ramp window. Attainment below plan
during ramp is expected. `expected_attainment_pct` vs `actual_attainment_pct` and
`status` (`ahead` / `on_track` / `behind` / `no_quota`) give the like-for-like read.

### 3b — The benchmark itself is survivorship-biased

`ramp_cohort` covers only reps **currently in their ramp window**. Every rep who left
during ramp is excluded. The observed cohort curve is therefore built from survivors and
is biased optimistic — measuring a struggling rep against it measures them against a
population that has already had its worst performers removed.

Attrition tracking is not instrumented in the platform. This bias cannot be corrected
today; it can only be disclosed.

Live: **one rep** in ramp. `cohort_median_attainment_pct` = 3.79% =
that rep's own `actual_attainment_pct`, because they are the entire cohort.

| Cohort n | Treatment |
|---|---|
| n = 1 | **Do not present a cohort median.** It is the rep's own number reflected back. |
| n < 5 | Present with n stated inline; do not call it a benchmark. |
| n ≥ 5 | Present with the survivorship caveat. |

Mandatory adjacent wording wherever a ramp figure appears:

> Ramp comparisons cover reps currently within their ramp window (n=N) and exclude
> anyone who left during ramp. The benchmark is therefore a survivor cohort and reads
> optimistic. Read as a best case, not an average.

`ramp_cohort` is manager-gated; ICs receive an empty payload plus a
`requires_manager_role` warning. On an empty payload, record that ramp status could not
be established — do not infer the rep is fully ramped.

---

## Screen 4 — Role–motion fit

**Source:** `hunter_farmer_mix`.

A farmer-oriented rep in a hunting patch (or the reverse) may have a role-fit problem
rather than a capability problem. Same numbers, different decision.

Parsing traps, verified live:

- Share fields are returned as **decimal strings**, not numbers:
  `"0.3865958822464172668865637752"`. Cast before comparing.
- Zero is sometimes `"0E+2"` scientific-notation string. `float("0E+2")` handles it;
  string comparison against `"0"` does not.
- `classification` is one of `hunter` / `farmer` / `hybrid` / `unknown`.

**Coverage limitation.** Live: 8 of 17 reps classified `unknown` — below the closed-won
threshold for classification — and `farmer_count: 0` across the whole roster. So for
roughly half the team this screen returns nothing, and the absence of any farmer
classification means a hunter/farmer mismatch argument has no comparison group.

If the rep is `unknown`, state that role-fit could not be assessed and why (insufficient
closed-won volume in the rolling window). **Do not read `unknown` as "no mismatch".**
Absence of evidence is not evidence of fit, and in a dossier that distinction is the
whole point.

---

## Screen 5 — Evidentiary depth

The most important screen, and the one with no dedicated tool.

**Sources:** `coaching_development.diagnostic_history`, `.focus_metric_trend`,
`.development_goals`; `coaching_meeting_analytics.total_meetings`;
`coaching_agenda.status`.

`coaching_diagnostic` and `coaching_agenda` changed from *get or generate* to **read
stored**. Where no record was generated, they return an empty or `not_generated`
response — **not an error**. A dossier built on those responses renders empty sections
and looks like a rep with no coaching history, when the truth is a system with no stored
records.

Live on Staging for rep 94:

- `diagnostic_history`: **1 week** (not the documented 13)
- `focus_metric_trend`: `[]`
- `development_goals`: `[]`
- `coaching_model_usage`: `{}`
- `coaching_meeting_analytics.total_meetings`: **0**

And for rep 98, `coaching_agenda` returned:
`{"status": "not_generated", "session_id": 1175, "message": "No stored agenda is
available for this coaching session. Generate it from the Coaching dashboard first."}`

### The depth gate

Compute and render, before any performance content:

| Depth signal | Value |
|---|---|
| Weeks of stored diagnostic history | `len(diagnostic_history)` |
| Development goals on record | `len(development_goals)` |
| Meetings analysed | `total_meetings` |
| Documented interventions targeting this rep | see Screen 6 |
| Stored agendas available | count of sessions not `not_generated` |

Then gate the artifact:

- **Fewer than 6 weeks of history, or zero development goals, or zero meetings
  analysed** → the dossier opens with an **insufficient-evidence banner** and every
  downstream section is labelled provisional.
- **Zero across all four** → the dossier states that no documented coaching record
  exists and **stops before performance evidence**. Produce the record-state finding and
  nothing else.

Banner wording:

> **Evidentiary depth: 1 week of stored diagnostic history, 0 development goals, 0
> meetings analysed, 0 rep-scoped interventions on record.**
> This is a record of what the system has stored, not a record of what coaching
> occurred. Coaching delivered outside the platform will not appear here. On this depth
> the material below cannot support a performance conclusion, and specifically cannot
> answer "what did you do to help them before this?".

That question — the one that ends the *manager's* career rather than the rep's — is
answered by the depth screen or it is not answered at all. Surfacing a thin record is the
single most valuable thing this dossier does, because a manager who learns it two weeks
before an HR meeting can still fix it. One who learns it in the meeting cannot.

---

## Screen 6 — What the Intervention Ledger actually covers

**Source:** `list_interventions`, `get_intervention_outcome`.

**The ledger is not rep-scoped.** Verified live: across 12 records, `entity.type` values
are `account`, `opportunity`, `source`, and `lead`. There is no `rep` entity type, and
`entity_type`/`entity_id` are the only entity filters available.

This matters because the rebuild plan lists `list_interventions` and
`get_intervention_outcome` as sources for "documented interventions and outcomes" in a
rep dossier. They cannot serve that purpose. The ledger records **deal and account
interventions**, not coaching delivered to a person.

What it can legitimately support: filtering client-side on `owner_id == rep_id` gives
interventions **assigned to** that rep — an execution-accountability signal. Label it
exactly that way:

> Interventions assigned to this rep: N open, M completed. This is deal-execution
> follow-through, not a record of coaching delivered to the rep.

Never present owner-filtered ledger records as coaching history. Two different things
with two different implications for a promotion or PIP decision.

### Outcome labels and causal framing

Records carry `correlation: {"basis": "correlational", "causal_claim_supported": false}`
and an `outcome.label` that takes values like `"worked"`.

`"worked"` is the ledger's own label for movement observed inside a bounded window. It
is not a finding that the intervention produced the movement. Render as:

> Intervention 7 (Southern Bank Corporation, health-score degradation): account health
> 0.46 → 0.50 across the 30-day outcome window. The ledger labels this "worked"; the
> record is correlational and does not establish that the intervention caused the change.

Also honour `outcome.status` and `window.state`. Live, most records show
`missing_reason: "completion_not_recorded"` and `state: "pending"` — the intervention was
never marked complete, so no outcome window ever opened. Report those as **not measured**,
never as failed. An unrecorded completion is a process gap, not a rep failure, and
scoring it against the rep would be exactly the kind of inference a grievance process
is designed to catch.

---

## Output contract

The screens produce a single ordered block that appears **before** any performance
evidence:

1. Evidentiary depth (Screen 5) — with the banner if the gate trips.
2. Structural factors identified (Screens 2, 3, 4) — each with its quantified effect
   where the data supports one, or an explicit "could not be assessed".
3. Signal reliability (Screens 1, 6) — base rates, ties, ledger scope limits.

Each entry states: what was checked, what was found, and **what it means for the weight
the performance evidence can carry**. That third part is the one that does the work.

If a screen cannot be run because a tool was unauthorised or returned empty, that is
itself a finding. Record it as *not assessed* with the reason. A screen silently skipped
is indistinguishable, later, from a screen that passed.
