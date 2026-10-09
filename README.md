# Indaga MCP and plugins

Connect your own Indaga account to an AI assistant and review recorded sources,
recovery evidence and dated lab results. The default **Indaga** plugin contains
these three workflows and the hosted MCP connection. **Indaga Weekly** is a
separately installed instruction-only plugin for wearable comparisons.
This repository does not contain a self-hosted Indaga server.

Version `0.2.7` is a release candidate. Installation, native account sign-in,
workflow acceptance and public directory approval are separate checks. Splitting
weekly instructions does not establish eligibility for either host's directory.

## Install the main plugin

Versioned ZIP and `.plugin` assets are published after review in
[GitHub releases](https://github.com/indaga-ai/indaga-plugins/releases).
A release asset is separate from a directory listing.

In Claude chat or Cowork, open **Customize → Plugins → Add → Add marketplace**
and enter `indaga-ai/indaga-plugins`. Select **Indaga** and choose **Add**.
Use its Connectors tab to finish hosted Indaga sign-in and consent.
Host versions, plans and organization settings can affect these controls.

In Claude Code:

```text
/plugin marketplace add indaga-ai/indaga-plugins
/plugin install indaga@indaga
```

Use `/mcp` to authenticate, then try `/indaga:record`, `/indaga:recovery` or
`/indaga:labs`. The main plugin does not contain a weekly skill.

For Codex, add this repository as a plugin marketplace, select **Indaga** and
complete its hosted connection's OAuth sign-in. The catalogue is at
`.agents/plugins/marketplace.json`; the main plugin is in `indaga/`.

## Add weekly separately

Install **Indaga Weekly** from the same marketplace or use the versioned
`indaga-weekly-0.2.7.zip` / `.plugin` asset. It contains only weekly instructions
and local references, with no MCP registration or separate sign-in.

In Claude Code:

```text
/plugin install indaga-weekly@indaga
```

Then request `/indaga-weekly:weekly`. The Claude manifest declares a main-plugin
dependency at `~0.2.7`: compatible `0.2.x` versions at least `0.2.7`. Host dependency
resolution does not prove the loaded main version or authenticated connection.
Verify both before using weekly. In Codex and other hosts, install the main plugin
explicitly first, then add **Indaga Weekly**. If main is missing, older,
incompatible or unconnected, weekly stops and asks you to install/update and
connect main. The [weekly connection guide](indaga-weekly/references/connection.md)
contains this requirement. No portable or Codex dependency field is invented.

[Standalone skill archives](docs/optional-skills.md) remain available for selected
instruction uploads. They are different from plugin archives and register no MCP
connection. Avoid installing two copies of the same workflow's instructions.

## Connect the hosted MCP

The main plugin registers `indaga-public-workflows` at
`https://app.indaga.ai/v1/mcp/public-workflows`.
[Connect Indaga to Claude](https://claude.ai/customize/connectors?modal=add-custom-connector&connectorName=Indaga&connectorUrl=https%3A%2F%2Fapp.indaga.ai%2Fv1%2Fmcp%2Fpublic-workflows)
opens a custom connector with its name and URL filled in. Complete sign-in and
consent through the host. This custom connection route alone does not install
plugin instructions or satisfy weekly's installed-main requirement. Use one
public connection; do not add a duplicate if the main plugin already supplies it.
In another MCP client, configure this URL as a Streamable HTTP server with OAuth.
Do not paste tokens into prompts, files or command-line headers.

## Scope and data handling

The four procedures across the two plugins are for adults reviewing their own
consumer wellness record. They preserve dates, units, coverage and uncertainty.
They provide wellness information, not diagnosis or treatment. An Indaga account
with Connect access is required. Missing measurements do not establish normal
results. Procedures and evidence references are contained in their installed
owner; the plugins do not download behavioral guidance.

The hosted public connection still exposes six read tools, including
`weekly.delta`, even when weekly is not installed. Its OAuth Connect credential
retains the usual broader grant, including recording and plan/routine changes
through other Indaga MCP surfaces. Splitting or selecting instructions does not
narrow that grant. Review consent permissions and use the public connection for
these workflows. Modular packaging does not change the health-information use
case or guarantee directory eligibility.

Your chosen AI provider receives the health and genetic information it reads
under its terms and privacy policy, and may process it outside the EU. Revocation
stops future access without deleting copies already received by the provider.
Neither plugin contains account credentials or personal records.

## Compatibility and support

Both plugins use public contract `1.0.0`. See the main
[connection guide](indaga/references/connection.md) and
[releases and updates](docs/releases.md). Every call supplies the contract version;
the server rejects unsupported versions before personal reads. The workflows
still verify briefing compatibility and preserve evidence limits. Native model
compliance is a separate acceptance check. Private document edits do not change
this contract.

[Support](https://app.indaga.ai/support) · [Privacy](https://app.indaga.ai/privacy) ·
[Terms](https://app.indaga.ai/terms). Contact support@indaga.ai.
Licensed under [AGPL-3.0-or-later](LICENSE).
