---
name: recovery
description: Review the signed-in person's dated Indaga recovery evidence and the engine's training ceiling relative to recent sessions. Use when asking how recovered I am or about today's recorded training limit.
metadata:
  mode: read-only
---

# Review recovery and training limits

Follow [connection and compatibility](../../references/connection.md), including
the initial briefing and server-contract check. Apply the
[evidence rules](../../references/evidence.md).

Read `recovery.state({"public_contract":"1.0.0"})`.
For a question about training today, also read
`decision.ceiling({"public_contract":"1.0.0"})`.
Both operations take only the required `public_contract` version. Explain the results separately at the scope
supported by each result's envelope; do not derive a ceiling from a readiness label.

Keep `latest_date`, state, paired/input-day coverage and returned qualifications
with the recovery result. Empty or calibrating history does not establish
readiness. Pattern names such as functional fatigue or overreaching do not
diagnose a syndrome. An old readiness label is historical, not today's training
assessment.

The ceiling uses its own recovery composite and recent-session reference.
Insufficient evidence or reference sessions can withhold it or leave it
calibrating. Explain that uncertainty rather than inventing a workload. Preserve
the returned `headline`, `undershoot_ok`, `undershoot_note`, reference-session
limits and supported reason. A ceiling is an upper bound, not a target or an
obligation to reach it. Do not replace a relative limit with a fabricated
heart-rate zone, duration, absolute load or recovery band.

This workflow reads only. It does not set goals, log a workout, edit the plan or
create a routine. A missing, stale or `not_measured` signal is unknown, never a
green light to train harder.
