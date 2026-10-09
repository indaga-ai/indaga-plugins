# Maintaining the hosted plugin

## Private review and public release mirror

`indaga-ai/indaga-plugins` is the public release mirror. Prepare changes in private
staging through reviewed PRs and green CI. Export only the approved tracked public
tree, without staging Git history, refs, handoffs or untracked files. Initialize
the first mirror snapshot with the company author and committer
`Indaga <support@indaga.ai>`; later updates use new company-authored snapshot
commits. Record the approved private source head, public snapshot head and tree
comparison in the private handoff. Do not copy private PR or merge refs to the
mirror or use its source history as the publication mechanism.

Run the mirror's package CI at its exact public head before release. Rebuild assets
from that clean public commit: their `release.json.source_commit` must identify
the public snapshot, not the private review commit. Candidate receipts remain
private until rebuilt and verified. Keep published version tags immutable.
Source publication, release assets and directory submissions are separate actions.

The contract-update proposal job runs only in private repositories. Its schedule
and manual dispatch skip the proposal job on the public mirror. Public package CI,
hosted compatibility checks and the reviewed draft-release workflow remain
available; no cross-repository update token is required. Future changes repeat
private review, company-authored public snapshot, exact-head CI and release
acceptance. Enabling workflow files does not prove those jobs have succeeded.

## Hosted contract updates

The hosted public contract is the authority for this bounded integration. Its
anonymous JSON projection is vendored in both `indaga/references/public-contract.json` and
`indaga-weekly/references/public-contract.json`.
`compatibility.json` records the version required by the installed workflows.
Compatible private document or unrelated server changes do not require a plugin
release. Breaking public behavior needs a new contract version and a reviewed
client update; keep the previous public version supported during rollout.

`Review hosted contract changes` checks the anonymous hosted projection daily and
on manual dispatch. It opens or updates one PR when that projection changes,
proposing a shared plugin patch version and updating the weekly Claude dependency
minimum. Both projection copies and both host-manifest/marketplace versions move
together; workflow bodies and required public-contract versions are unchanged. It never imports behavioral guidance, changes
the required workflow version, merges, publishes or deploys. Inventory or format
changes fail and require manual review. Unsupported installed versions fail the
package compatibility gate until reviewers migrate the workflows explicitly.

In private staging, GitHub Actions must be allowed to create pull requests by
both organization policy and repository settings. The earlier HTTP409 policy
block there was resolved on 2 October 2026 with explicit publisher approval;
workflow defaults remained read-only. Repository settings are not copied with
the source tree. The public mirror does not need PR creation enabled because
its proposal job is skipped. The updater does not approve, merge or publish PRs.

Until the hosted contract is deployed and successful job execution is recorded,
the automatic update path remains unverified. As a manual fallback, a maintainer can run
`python3 scripts/check_hosted_contract.py --update` in an isolated branch,
review the resulting public diff, commit it, and create a PR with their existing
authenticated GitHub CLI. This is a manual update path, not a successful scheduled
job. Actual update and draft-release job receipts remain release acceptance gates.

The update job explicitly dispatches package checks for its branch because events
created with the repository token do not automatically trigger PR checks. Keep
`Public package checks / package` required before merging. Review operation schemas,
evidence behavior and affected native workflows before approving the update.
Production server rollout belongs to its product release owner.

For a release:

1. Merge the reviewed public client PR with green package CI. Record genuine native
   installation, OAuth sign-in and four-workflow acceptance in the private project
   handoff. Static validation cannot substitute for that proof.
2. Run `Draft reviewed release` from `main`, supplying its exact manifest version.
   It rechecks schemas, archives, host manifests and hosted compatibility. The
   hosted check uses no account token and does not read personal data.
3. Inspect the draft assets and private acceptance receipt. Publish the draft only
   after acceptance. The publication helper creates `v<version>`,
   `indaga--v<version>` and `indaga-weekly--v<version>` at the same approved public
   commit before creating a draft with `--verify-tag`. Each reference creation is
   atomic; the three reservations are not a transaction. The per-plugin aliases
   support Claude's documented dependency-version resolution for relative
   marketplace sources. An existing tag of any of these names, even without a
   release, refuses the job before artifact upload.
   Directory submissions remain separate.

If a later tag reservation, draft creation or upload fails, earlier reserved tags
remain. No draft upload occurs until all three reservations succeed.
The job never overwrites or deletes it automatically. A maintainer must inspect the
remote tag's exact commit and the existing draft/assets against the approved source
and receipt before a reviewed manual recovery. Use a new version or deliberately
complete that exact draft; an unchanged blind rerun will fail safely. Never move an
old release or per-plugin tag to make a rerun pass. The general release history
is retained. See [Claude's dependency release tags](https://code.claude.com/docs/en/plugins/dependencies#release-a-plugin-that-others-depend-on).

Local equivalent: `python3 scripts/release.py validate`,
`python3 -m unittest discover -s tests -v`, and
`python3 scripts/release.py build`. Build from a clean committed public tree.
Each plugin archive includes only its own tracked files under `indaga/` or
`indaga-weekly/`, keeps both host manifest directories, and places that plugin
at the archive root. Main contains only record, recovery and labs, with the sole
MCP registration. Weekly contains only weekly and local references, license,
icons and manifests, without transport or authentication. Fixed file modes/timestamps
and uncompressed ZIP entries make artifact bytes reproducible across platforms.
Each plugin's `.zip` and `.plugin` assets are identical; verify all eight payloads
with `SHA256SUMS`. `release.json.plugin_archives` records each plugin's owner,
workflow set, ZIP/.plugin hashes and exact canonical file hashes, without plugin
transformations. `source_commit` binds both plugins and the four standalone packs
to the reviewed public source. Existing released tags remain immutable.

The same build also emits four instruction-only standalone skill ZIPs. Each has
one namespaced skill folder, contained connection/evidence/contract references,
license and installation README. The build adapts only standalone names, local
links, upload-description length and connection-guide containment wording; it
records every transformation and file/archive hash in `release.json`. Standalone
packaging does not alter either plugin's canonical procedural bodies. Each skill
comes from its actual owner: main for record/recovery/labs, weekly addon for weekly.
Weekly's standalone guide retains the installed-main dependency and does not
claim that the skill ZIP declares or installs a plugin dependency.
Existing draft-release ZIP selection includes these sidecar assets. See [optional-skill installation](optional-skills.md).
Packaging proof does not establish successful upload, host dependency behavior or
authenticated native acceptance for a standalone pack.

Schema checks use reviewed SHA-256 pins for the official portable schemas.
Host validation pins the Claude CLI version. Update those pins through a reviewed
PR when their upstream contracts change.

# Updating an installed plugin

Marketplace source updates do not prove that a running host loaded the new package.
Use the host's plugin update controls, then fully restart the host if its displayed
version or behavior stays old. In Claude Code, use `/plugin update indaga@indaga` and, if installed,
`/plugin update indaga-weekly@indaga`, then start a fresh session. For Claude chat/Cowork and Codex, check the installed
plugin's version in its details, update/reinstall from the marketplace if needed,
and restart the application. Follow the host's current supported controls.

Confirm each installed version matches its released manifest. Main discovers
record/recovery/labs; weekly is available only when separately installed. Weekly
requires compatible main `~0.2.7` and main's authenticated connection. Claude
dependency resolution alone does not prove loaded bytes, version or sign-in.
Codex requires explicit main installation. Establish a new sign-in if the endpoint changed.
Do not copy an OAuth token from the old connection. The first workflow call must
confirm supported public-contract compatibility; old or local tools are a stop,
not permission to fall back. For QA, compare the installed manifest and skill file
hashes with `release.json`; a displayed catalogue version alone is insufficient.

Anthropic marketplace distribution and OpenAI directory uploads have separate
update paths. A GitHub release does not claim either directory approval or that an
already running host has refreshed its plugin cache.
