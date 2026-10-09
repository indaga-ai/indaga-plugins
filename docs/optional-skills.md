# Install selected Indaga workflows

The main [Indaga plugin](../README.md#install-the-main-plugin) contains the hosted
connection and record, recovery and labs procedures. The optional **Indaga Weekly**
plugin contains weekly only and reuses main's connection. These standalone skill
ZIPs are an alternative instruction upload route for selected workflows. They do
not automatically install another plugin, configure MCP or authenticate an account.

Versioned release assets include:

| Skill archive | Workflow |
| --- | --- |
| `indaga-record-skill-0.2.6.zip` | Recorded sources, date ranges and missing inputs |
| `indaga-weekly-skill-0.2.6.zip` | Weekly wearable comparisons |
| `indaga-recovery-skill-0.2.6.zip` | Recovery evidence and training-ceiling limits |
| `indaga-labs-skill-0.2.6.zip` | Named dated results and panel coverage |

Download assets from the [reviewed release](https://github.com/indaga-ai/indaga-plugins/releases)
when published. A source checkout or prepared archive does not establish directory
approval or authenticated workflow acceptance. No DNA workflow is included.

## Connection first

Use an existing Indaga public-workflow connection to
`https://app.indaga.ai/v1/mcp/public-workflows`. An Indaga account with Connect
access is required. Complete sign-in and consent through the host's normal UI;
do not paste credentials or OAuth tokens into chat. The workflow must discover
the named public tools and verify contract `1.0.0` before interpreting records.
An old dispatcher or similarly named local server is not a compatible connection.

In Claude, [add the hosted connector](https://claude.ai/customize/connectors?modal=add-custom-connector&connectorName=Indaga&connectorUrl=https%3A%2F%2Fapp.indaga.ai%2Fv1%2Fmcp%2Fpublic-workflows)
if it is absent, then complete OAuth. In Codex, use the host's supported MCP
connection controls to configure that URL if absent. Installing a skill does not
make the connector's tools available in every client or session: confirm the
connection is enabled where you will use the skill.

Use one connection. Weekly, including its standalone skill pack, requires the
installed main plugin at `~0.2.6` (compatible `0.2.x` versions at least `0.2.6`)
and its authenticated connection. If absent or incompatible, install/update and
connect main first. Do not add a standalone copy of a workflow already supplied
by an installed plugin. A standalone pack declares no plugin dependency and
does not install one automatically.

## Claude chat and Cowork

1. Open **Customize → Skills → + → Create skill → Upload a skill**.
2. Upload the selected skill ZIP without unpacking it, then enable it.
3. Start a conversation with the hosted Indaga connector enabled and request the
   installed workflow, for example: “Use Indaga weekly to review this week's
   recorded changes.”

The ZIP contains one folder whose name matches the skill's frontmatter name,
such as `indaga-weekly/SKILL.md`, plus its contained references and license.
Skill creation and code execution can depend on your plan and organization
settings. This route is a custom upload, not an Anthropic directory listing.
See [Claude's custom-skill instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
For Claude Code, the main and optional weekly plugin installations in the root
README are the documented plugin route. Standalone skill uploads do not inherit
the weekly plugin's Claude dependency declaration.

## Codex local skills

Extract the archive's `indaga-<workflow>/` folder into either:

- Your user skill directory: `~/.agents/skills/`.
- Your repository skill directory: `.agents/skills/`.

For example, from the directory containing the downloaded assets, verify the
release checksums and install weekly only if its destination does not exist:

```sh
shasum -a 256 -c SHA256SUMS
mkdir -p ~/.agents/skills
test ! -e ~/.agents/skills/indaga-weekly && \
  unzip indaga-weekly-skill-0.2.6.zip -d ~/.agents/skills
```

Keep all downloaded assets alongside `SHA256SUMS` for that checksum command. If
you downloaded only one ZIP, compare its hash with its entry in `SHA256SUMS`.
If the destination exists, inspect the installed version before updating it;
do not unpack a new version over it without reviewing the replacement.
Start a new Codex session, select `indaga-weekly` from the skill picker and ensure
the existing hosted connection is available. Host versions and organization
settings can affect discovery. See [OpenAI's local-skill documentation](https://learn.chatgpt.com/docs/build-skills).

## Permissions and updates

These packs contain instructions, not access controls. All six public tools
remain available to the authorized connection. Its OAuth credential retains the
usual broader grant, including writes through other surfaces; selecting a pack
does not narrow that grant. Each pack permits only its contained read workflow
and retains own-account, date, evidence and no-write guards.

They are for adults reviewing their own consumer wellness record, not diagnosis
or treatment. Your chosen AI provider receives the information it reads under
its terms and privacy policy and may process it outside the EU. Revoking a
connection stops future access without deleting copies already received by the
provider. [Privacy](https://app.indaga.ai/privacy) and [support](https://app.indaga.ai/support).

Each pack is self-contained and never downloads behavioral instructions at
runtime. To update a standalone skill, review the new asset and checksum, then
replace that skill through the host's supported controls and start a new session.
The pack README records its source package version; `release.json` records the
source commit, canonical plugin owner, archive/file hashes and every packaging
transformation. Record, recovery and labs come from `indaga/`; weekly comes from
`indaga-weekly/`. Connection and skill installation are separate from sign-in,
acceptance and directory
review. No one-click cross-client installation or new native acceptance is
claimed by these packaging checks.
