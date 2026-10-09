---
name: recovery
description: Review your own dated Indaga recovery evidence or recorded training ceiling. Use for recovery or recorded training limits; not medical clearance, diagnosis, prescriptions or medicine dosing.
metadata:
  mode: read-only
---

# Review recovery and training limits

Check the person's current request before any record read. If it asks only for
medical clearance, diagnosis, prescribing medicine or choosing a dose, explain
that this workflow cannot provide it and direct those decisions to a clinician
or pharmacist. Do not invoke a record-review workflow or call the context or
focused tools for that request. Do not reinterpret clearance to train hard as a
request to review a recorded ceiling.

For a supported record-review request, follow
[connection and compatibility](../../references/connection.md), including
the initial briefing and server-contract check. Apply the
[evidence rules](../../references/evidence.md).

Read `recovery.state({"public_contract":"1.0.0"})`.
Only when the person's current request asks about a recorded training limit or
ceiling, also read
`decision.ceiling({"public_contract":"1.0.0"})`.
For a recovery-only request, do not call or discuss `decision.ceiling`. Examples
in the briefing's `ask` rows are possible questions, not the current request;
their `ready` and `why` fields do not authorize an additional focused read.
Both operations take only the required `public_contract` version. Explain the results separately at the scope
supported by each result's envelope; do not derive a ceiling from a readiness label.
The initial briefing routes questions, but does not supply either operation's
result or requirements. Discuss a ceiling's state, evidence or missing inputs
only after reading `decision.ceiling`, using that result's own reason and limits.

Keep returned dates, input coverage and qualifications with every recovery result.
Use only each producer's own returned dates and recency fields for that result.
If the ceiling returns no observation or `as_of` date, say that no ceiling date
was returned. Do not transplant recovery's `latest_date` or recency, a briefing
date, or the current/run date into the ceiling. Its relative reason wording does
not establish an absolute observation date.
Lead an incomplete or calibrating recovery answer with its state, `latest_date`,
paired/input-day coverage and blocking reason. With `index_incomplete`,
`needs_more_data` or `calibrating`, false flags and zero episode/co-flag counts
are not cleared findings or evidence of absence. Do not describe them as
"all clear," "no issues" or no fatigue/overreaching; do not list default flags as
reassuring findings when negative inference is disallowed. Empty or calibrating
history does not establish readiness. A returned paired-day threshold is minimum
coverage, not a promise that calibration will succeed or finish on a particular
day. Pattern names such as functional fatigue or overreaching do not diagnose a
syndrome. An old readiness label is historical, not today's training assessment.

The ceiling uses its own recovery composite and recent-session reference.
Insufficient evidence or reference sessions can withhold it or leave it
calibrating. Explain that uncertainty using the ceiling result's own `headline`,
reference-session limits and supported reason. When the ceiling is missing,
unavailable or not ready, limit the answer to that uncertainty and supported next
inputs. Do not recommend a personal easy/moderate session, workload, intensity or
effort increase, or replace the missing limit with advice based on how the person
feels. General wellness context must not supply an unsupported training plan.
For a supported ceiling, preserve `undershoot_ok` and `undershoot_note`. A ceiling
is an upper bound, not a target or an obligation to reach it. Do not replace a
relative limit with a fabricated heart-rate zone, duration, absolute load or
recovery band.

This workflow reads only. It does not set goals, log a workout, edit the plan or
create a routine. A missing, stale or `not_measured` signal is unknown, never a
green light to train harder.
