# Indaga MCP and plugins

Connect your own Indaga account to an AI assistant and review recorded sources,
weekly wearable changes, recovery evidence and dated lab results. This repository
contains a hosted MCP connection and four public workflow skills for Claude and
Codex. It does not contain a self-hosted Indaga server.

The package is a release candidate. Public directory listing, native account
sign-in and full workflow acceptance are not established by a valid manifest.

## Connect the hosted MCP

[Connect Indaga to Claude](https://claude.ai/customize/connectors?modal=add-custom-connector&connectorName=Indaga&connectorUrl=https%3A%2F%2Fapp.indaga.ai%2Fv1%2Fmcp%2Fpublic-workflows)
opens Claude with the connection name and URL filled in. Confirm adding it, then
complete Indaga sign-in and consent. This installs the connection; install the
plugin below to add the four workflows.

The hosted endpoint is `https://app.indaga.ai/v1/mcp/public-workflows`. In another MCP client, add
this URL as a Streamable HTTP server and use its OAuth sign-in flow. Do not paste
tokens into prompts, source files or command-line headers.

## Install the plugin

After public release, versioned archives will appear in the repository's
[GitHub releases](https://github.com/indaga-ai/indaga-plugins/releases). A release
asset is separate from a directory listing.

In Claude chat or Cowork, open **Customize → Plugins → Add → Add marketplace**
and enter `indaga-ai/indaga-plugins`. Select Indaga and choose **Add**. Connect the
Indaga connector from the plugin's Connectors tab if needed. A future public
directory listing will provide a shorter Add-button installation path.

In Claude Code:

```text
/plugin marketplace add indaga-ai/indaga-plugins
/plugin install indaga@indaga
```

Use `/mcp` to finish the hosted connection's sign-in. Then try `/indaga:record`,
`/indaga:weekly`, `/indaga:recovery` or `/indaga:labs`.

For Codex, add this repository as a plugin marketplace, select Indaga and complete
the hosted connector's OAuth sign-in. The catalogue is at
`.agents/plugins/marketplace.json`; the plugin is in `indaga/`. Host versions and
organization settings can affect which installation options are available.

For an existing hosted connection, [standalone skill archives](docs/optional-skills.md)
let you install selected workflows through Claude's custom-skill upload or Codex's
local skill directory. They contain instructions only and do not narrow the
connection's permissions. The complete plugin remains the simplest starter.

## Scope and data handling

These four workflows are for adults reviewing their own consumer wellness record.
They preserve dates, units, coverage and uncertainty. They provide wellness
information, not diagnosis or treatment. An Indaga account with Connect access is
required. Missing measurements do not establish normal results.

The public workflow endpoint exposes six read tools. Its OAuth Connect credential
retains the usual broader grant, including recording and plan/routine changes
through the legacy Indaga MCP surface. This package does not narrow the OAuth
grant. Review the permissions shown during consent and use the public workflow
endpoint for these workflows.

Connecting allows your chosen AI provider to receive the health and genetic
information it reads, under that provider's terms and privacy policy. Providers
may process that information outside the EU. Revoke the connection in Indaga to
stop future access; revocation does not delete copies already received by the AI
provider. The plugin contains no account credentials or personal records.

## Compatibility and support

Version `0.2.5` uses a small, self-contained set of public procedures. Its required
public contract is documented in [the connection guide](indaga/references/connection.md).
Each call supplies the required public-contract version; the public endpoint rejects
unsupported versions before personal reads. The workflows also require a briefing
compatibility check and preserve evidence limits. Native model compliance remains
a separate acceptance check. Private document edits do not change this contract.
See [releases and installed-plugin updates](docs/releases.md) for the reviewed
contract update process and version/cache verification.

[Support](https://app.indaga.ai/support) · [Privacy](https://app.indaga.ai/privacy) ·
[Terms](https://app.indaga.ai/terms). Contact: support@indaga.ai.

This package is licensed under [AGPL-3.0-or-later](LICENSE).
