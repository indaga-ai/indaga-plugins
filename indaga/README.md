# Indaga

The default main plugin contains three read-only procedures: recorded sources
and gaps, dated recovery evidence and named lab results or panel coverage.
An adult reviews their own record with an Indaga account and Connect access.
Weekly comparisons are the separately installed **Indaga Weekly** plugin.

Install main from its marketplace or upload `indaga-0.2.7.plugin` / ZIP through
Claude's supported plugin upload controls. Complete the hosted connection's
sign-in and consent. In Claude Code, use `/mcp`, then `/indaga:record`,
`/indaga:recovery` or `/indaga:labs`. Main does not contain `/indaga:weekly`.

Main registers `indaga-public-workflows` at
`https://app.indaga.ai/v1/mcp/public-workflows`. Version `0.2.7` contains its
procedures and does not download behavioral guidance. See the
[connection guide](references/connection.md) for the reviewed public contract.
Every tool call passes the required version; unsupported versions are rejected
before personal reads. Preserve evidence limits and verify briefing compatibility.
Manifest validation does not establish native sign-in, workflow acceptance or
directory approval.

The connection still exposes six read tools, including `weekly.delta`. Its OAuth
Connect credential retains the usual broader grant, including writes through
other Indaga MCP surfaces. Splitting instructions does not narrow that grant or
establish directory eligibility. Review consent permissions. Your chosen AI
provider receives health and genetic information it reads under its terms and
privacy policy, and may process it outside the EU. Revocation stops future access
without deleting provider copies.

Wellness information, not diagnosis or treatment. Keep dates, units and missing
inputs with each answer. [Support](https://app.indaga.ai/support),
[Privacy](https://app.indaga.ai/privacy), [Terms](https://app.indaga.ai/terms).
Contact support@indaga.ai. Licensed under [AGPL-3.0-or-later](LICENSE).
