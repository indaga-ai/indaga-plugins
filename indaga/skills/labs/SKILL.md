---
name: labs
description: Review a named lab result or requested panel's measurement coverage in the signed-in person's Indaga record. Use for stored blood results, draw dates, lab history or missing panel measurements.
metadata:
  mode: read-only
---

# Review dated lab results

Follow [connection and compatibility](../../references/connection.md), including
the initial briefing and server-contract check. Apply the
[evidence rules](../../references/evidence.md).

For a named result, call
`labs.query({"public_contract":"1.0.0","analyte":"<normalized analyte name>"})`.
The `analyte` value is a string. If the requested analyte is ambiguous, ask which
one the person means rather than guessing or omitting the filter to read all labs.
Do not add `flagged_only`: the server ignores it for a named-analyte query. Explain
all returned dated results at their supported scope, without calling an empty
answer normal or a complete panel.

For panel coverage, call
`labs.panel_coverage({"public_contract":"1.0.0","analytes":["<requested normalized analyte>"]})`.
`analytes` is an array of strings. Use the analytes the person requested, asking
for clarification when the panel name is ambiguous. If they request the server's
default panel, omit `analytes` and use the returned panel definition. Do not
invent a panel or imply that a missing analyte was tested.

Keep each returned value with its recorded draw/observation date, unit, source,
entry method and assay-specific reference information. Honor `is_stale` and
recency qualifications where returned. A document's date is not necessarily a
draw date. An old value is a result from that date, not the person's current
value. Do not invent a date, silently convert units or infer a flag the record
does not provide. Keep person-stated measurements distinct from source-verified
measurements.

Explain the envelope's supported scope and panel gaps without diagnosing a
condition or choosing treatment. This workflow makes no writes or corrections.
Direct requests to add, confirm, discard or correct a result to the Indaga app;
do not call those operations through another connection.
