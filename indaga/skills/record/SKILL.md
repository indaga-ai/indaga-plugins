---
name: record
description: Explain what the signed-in person's Indaga record contains, its recorded sources and date ranges, and which questions it can answer. Use when getting started or asking what Indaga knows about me.
metadata:
  mode: read-only
---

# Understand my Indaga record

Follow [connection and compatibility](../../references/connection.md), including
the initial `indaga.describe_context({"public_contract":"1.0.0"})` call and server-contract check. Apply
the [evidence rules](../../references/evidence.md).

Use the briefing's `record.holds`, `ask` and `record.not_here` to explain recorded
sources, returned date spans, supported questions and missing inputs. Report only
the inventory and gaps it actually returns. Distinguish an unavailable source
from a connected source with insufficient measurements.

The briefing maps what the record holds; it does not establish a health finding.
Do not read raw series or lab values merely to enlarge this inventory. When the
person asks a question covered by weekly, recovery or labs, use that installed
workflow. Otherwise explain the limit of this plugin.

This workflow only calls `indaga.describe_context` with `public_contract: "1.0.0"` and no subject selector. It does
not import data, change the record or choose another person's account.
