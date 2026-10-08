# Indaga

Four read-only workflows help an adult review their own Indaga record: recorded
sources and gaps, weekly wearable changes, dated recovery evidence and named lab
results or panel coverage. An Indaga account with Connect access is required.

Install this plugin from its marketplace or upload its `.plugin`/ZIP file through
Claude's Customize → Plugins → Add → Upload plugin. Complete the hosted Indaga
connection's sign-in and consent. In Claude Code, use `/mcp` to authenticate, then
try `/indaga:record`, `/indaga:weekly`, `/indaga:recovery` or `/indaga:labs`.

The endpoint is `https://app.indaga.ai/v1/mcp/public-workflows`. The procedures are contained in this
package and do not download behavioral guidance. Version `0.2.4` is a release
candidate; manifest validation alone does not establish native sign-in, workflow
acceptance or directory approval. The [connection guide](references/connection.md)
identifies the reviewed public contract. Every tool call passes the required
version; the public endpoint rejects unsupported versions before personal reads.
The assistant must still preserve evidence limits and verify briefing compatibility.
Model compliance remains a separate acceptance check.

The public workflow endpoint exposes six read tools. Its OAuth Connect credential
retains the usual broader grant, including writes through the legacy Indaga MCP
surface. This package does not narrow that grant. Review the consent permissions. The chosen AI
provider receives health and genetic information it reads under its own terms
and privacy policy, and may process it outside the EU. Revocation in Indaga stops
future access without deleting copies previously received by the AI provider.

Wellness information, not diagnosis or treatment. Keep dates, units and missing
inputs with each answer. [Support](https://app.indaga.ai/support),
[Privacy](https://app.indaga.ai/privacy), [Terms](https://app.indaga.ai/terms).
Contact support@indaga.ai. Licensed under [AGPL-3.0-or-later](LICENSE).
