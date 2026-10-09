---
name: weekly
description: Review changes in the signed-in person's Indaga wearable record across the latest two sets of seven observed days. Use for weekly check-ins about recorded HRV, sleep timing, recovery proxies or movement.
metadata:
  mode: read-only
---

# Review weekly changes

Follow [connection and compatibility](../../references/connection.md), including
the initial briefing and server-contract check. Apply the
[evidence rules](../../references/evidence.md).

Call `weekly.delta({"public_contract":"1.0.0"})`.
This operation takes only the required `public_contract` version. Use its returned comparison rather than
calculating a substitute from raw series.

For each supported row, state the exact current and prior periods, distinct-day
counts, values, units, `direction` and `descriptor`. The windows are the latest
seven days with data and the preceding seven; they can span more than two
consecutive calendar weeks. Different rows can have different windows and
readiness. Do not turn a calibrating or missing row into a steady result.

The direction describes the engine's favorable, unfavorable or steady
interpretation, rather than the numeric sign: `up` can accompany a lower number.
Use its descriptor and values together. The recovery row uses resting-heart-rate
observations rather than `recovery.score`; sleep regularity describes sleep
midpoint variability rather than the separate sleep-regularity index. Explain
these as the returned proxies.

Keep calibration, freshness, correction and import qualifications with each row.
Do not infer that a named behavior caused a change or combine the rows into an
unreturned health score. This workflow performs only the briefing and this focused
read. It does not create a brief, edit a plan or log an activity.
