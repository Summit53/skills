# Async Envelopes — Canonical Handling

**Canonical file. Version 2.0.1 · adapted for Summit53 Staging.**

> **v2.0.0 change.** The server now returns machine-readable completion instructions.
> **Read `job_lifecycle.completion` and follow it** rather than hard-coding the pattern
> below. The hard-coded pattern is retained as the fallback for any tool that does not
> yet emit the block, and as the explanation of *why* the instruction says what it says.

This file is maintained once and copied byte-identical into every skill that consumes an
async Summit53 tool. If you edit it, bump the version and re-copy to all consumers.
If two copies disagree, the higher version wins.

Consumers as of 2026-08-08: `forecast-delta-brief`, `board-revenue-pack`,
`rep-evidence-dossier`, `qbr-generator`, `territory-review`, `win-loss-analysis`,
`revenue-action-brief-s53`, `strategic-assessment-s53`.

## Contents

- [The failure this prevents](#the-failure-this-prevents)
- [Preferred path](#preferred-path-follow-job_lifecyclecompletion)
- [Poll then re-call](#the-critical-detail-get_job-does-not-return-your-payload)
- [Terminal states and budgets](#terminal-vs-non-terminal-job-states)
- [Missing and ready payloads](#when-the-source-is-genuinely-missing)
- [Reference implementation](#reference-implementation)
- [Other async surfaces](#other-async-surfaces)

---

## The failure this prevents

`unified_forecast_summary` does not always return data. On a cold cache it returns a
**processing envelope** instead:

```json
{"data": {"message": "Crunching your forecast — this can take a few seconds. Ask again in a moment.",
          "status": "processing",
          "job_id": "628b2e76-5d86-449e-a90a-7bcd77a31d0a",
          "retry_after": 5,
          "job_lifecycle": {"get":    {"tool": "get_job", "job_id": "..."},
                            "cancel": {"tool": "cancel_job", "job_id": "..."},
                            "retention_days": 30}},
 "warnings": ["processing"]}
```

A skill that reads this as its forecast payload finds no `primary`, no `kpis`, no
`quota_metrics` — and renders those sections empty. **It does not error.** It produces a
thin artifact and reports success. That is the specific failure mode this file exists to
prevent, and it is a demo-failure mode: the deck generates, the numbers are missing, and
nobody finds out until someone reads the slide out loud.

**Never treat a `processing` envelope as data. Never treat a missing field as a zero.**

---

## Preferred path: follow `job_lifecycle.completion`

As of the 8 Aug 2026 fix, the processing envelope carries explicit instructions:

```json
{"status": "processing", "job_id": "fb3ca5b3-…", "retry_after": 5,
 "completion_mode": "reinvoke_source_tool",
 "job_lifecycle": {
   "get":    {"tool": "get_job",    "job_id": "fb3ca5b3-…"},
   "cancel": {"tool": "cancel_job", "job_id": "fb3ca5b3-…"},
   "completion": {"mode": "reinvoke_source_tool",
                  "tool": "unified_forecast_summary",
                  "arguments": "identical_to_initial_call",
                  "when": "after_get_job_status_completed"},
   "retention_days": 30}}
```

The same `completion` block is echoed on the `get_job` response, at both the top level
and under `metadata`.

**Drive the handler from these fields.** Read `completion.tool`, `completion.when` and
`completion.arguments` rather than assuming. If a future job type introduces a different
`mode`, a handler that reads the field adapts; one that hard-codes `reinvoke_source_tool`
silently breaks — the exact drift class this whole remediation addressed.

Treat a missing `completion` block as `mode: "reinvoke_source_tool"` and proceed with the
fallback below.

`refresh: true` is now safe: it enqueues a single job and returns a normal processing
envelope. Verified — job `fb3ca5b3` completed in 1,997 ms with no requeue loop. Note it
**does recompute and persist** derived scores, so it is a write in practice. Do not call
it on a schedule from a read-only artifact.

---

## The critical detail: `get_job` does not return your payload

This is counter-intuitive and it is the single easiest thing to get wrong.

`get_job` returns **lifecycle state**, not the result you asked for:

```json
{"data": {"job_id": "628b2e76-...", "job_name": "revenue.unified_forecast.calculate",
          "status": "completed", "progress": {"message": "Completed", "percent": 100},
          "result": {"cached": true, "status": "success"},
          "error": null, "source_tool": "unified_forecast_summary",
          "created_at": "...", "completed_at": "...", "retention_days": 30}}
```

Note `result` is `{"cached": true, "status": "success"}` — a receipt, not a forecast.

So the pattern is **poll then re-call**, not poll-for-result:

1. Call the tool.
2. If `data.status == "processing"`, capture `data.job_id`.
3. Poll `get_job(job_id)` until `data.status` is terminal.
4. On `completed` — **call the original tool again, with identical arguments**. The
   computed result is now cached and it returns `status: "ready"` with the full payload.
5. On `failed` / `cancelled` — do not re-call. Treat as a missing source (see below).

Re-calling with identical arguments matters: the cache key includes the parameters. A
re-call with different `period_offset` or `detail_level` is a different job and will
start processing all over again.

---

## Terminal vs non-terminal job states

Poll while `status` is `queued`, `running`, or `pending`. Stop on `completed`,
`failed`, or `cancelled`. Treat any unrecognised status as non-terminal for up to the
attempt budget, then give up and declare the source missing — an unknown status is not a
reason to loop forever.

---

## Budget

- Wait `retry_after` seconds between polls. It is advisory; if absent, use 5.
- Cap at **6 poll attempts** (~30s at the default interval).
- Cap at **2 re-calls** of the original tool. If a re-call returns `processing` a second
  time, stop — something is wrong upstream and further polling will not fix it.

Exceeding either budget means the source is missing. It does not mean the source is zero.

---

## Overlap the wait

The poll is dead time. Fire every other independent tool call in the same batch as the
first `unified_forecast_summary` call, so the polling overlaps their execution rather
than serialising behind it. In practice the forecast is usually ready by the time the
other pulls return, and the poll costs nothing.

---

## When the source is genuinely missing

Do not silently omit the section. Do not substitute a stale figure without labelling it.
Render the section with an explicit statement of absence:

> **Forecast confidence — unavailable.** `unified_forecast_summary` did not return a
> completed result within the retry budget (job `628b2e76`, last status: `running`).
> This section is blank because the data could not be retrieved, not because the values
> are zero.

An artifact that says "I could not get this" is defensible. An artifact with a silently
empty section is not — and in a board or PIP context, the difference matters.

---

## Reference implementation

```python
import time, json

TERMINAL_OK   = {"completed"}
TERMINAL_FAIL = {"failed", "cancelled"}

def unwrap(resp):
    """Summit53 MCP responses arrive as {"result": "<json string>"} or already parsed."""
    if isinstance(resp, dict) and "result" in resp and isinstance(resp["result"], str):
        return json.loads(resp["result"])
    return resp

def resolve_async(call_tool, tool_name, args, get_job,
                  max_polls=6, max_recalls=2, default_wait=5):
    """
    Returns (payload_or_None, note).
    `call_tool(name, args)` and `get_job(job_id)` are thin MCP wrappers.
    """
    for recall in range(max_recalls + 1):
        body = unwrap(call_tool(tool_name, args)).get("data", {})

        if body.get("status") != "processing":
            return body, None                      # ready (or a tool with no async path)

        job_id = body.get("job_id")
        if not job_id:
            return None, f"{tool_name} returned a processing envelope with no job_id"

        wait = body.get("retry_after") or default_wait
        last = "unknown"

        for _ in range(max_polls):
            time.sleep(wait)
            job  = unwrap(get_job(job_id)).get("data", {})
            last = job.get("status", "unknown")
            if last in TERMINAL_OK:
                break                              # fall through to re-call
            if last in TERMINAL_FAIL:
                return None, (f"{tool_name} job {job_id} ended {last}: "
                              f"{job.get('error') or 'no error detail'}")
        else:
            return None, (f"{tool_name} job {job_id} still {last} after "
                          f"{max_polls} polls — treated as missing")

        # job completed; loop re-calls the tool with IDENTICAL args to collect the payload

    return None, f"{tool_name} still processing after {max_recalls} re-calls — treated as missing"
```

Carry every returned `note` into the artifact's data-sources section verbatim. A note is
evidence about the artifact's own reliability and belongs in the deliverable, not in a
log the reader never sees.

---

## Validating a "ready" payload

`status: "ready"` means the job finished, not that every field is populated. Before
rendering, confirm the specific fields you need are present and non-null. Two live
examples from Staging:

- `kpis.forecast_accuracy` returns all zeros with `trend: "no_forecasts"` — that is
  "never measured", not "0% accurate". Render it as *not yet measurable*.
- `revenue_at_risk.top_deals` came back as `[]` while `deal_count` was 24 — the count is
  real, the drill-down list is empty. Do not infer from an empty list that there are no
  deals.

`null` and `[]` are not zero. Say "not available" and move on.

---

## Other async surfaces

`segment_performance_summary` and `revenue_engine_context` also carry a `status` field
and may return `processing` under cache pressure. Route them through the same helper —
`resolve_async` is tool-agnostic. Tools that return `status: "ready"` immediately pass
through the first branch at no cost.

`revenue_engine_context` additionally accepts `fast_forecast: true` (the default), which
serves a cheaper forecast path and is less likely to enqueue a job at all. Prefer it for
breadth-first artifacts; use the granular `unified_forecast_summary` when one specific
authoritative number is being quoted.
