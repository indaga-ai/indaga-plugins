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
anonymous JSON projection is vendored in `indaga/references/public-contract.json`.
`compatibility.json` records the version required by the installed workflows.
Compatible private document or unrelated server changes do not require a plugin
release. Breaking public behavior needs a new contract version and a reviewed
client update; keep the previous public version supported during rollout.

`Review hosted contract changes` checks the anonymous hosted projection daily and
on manual dispatch. It opens or updates one PR when that projection changes,
proposing a plugin patch version. It never imports behavioral guidance, changes
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
   after acceptance. The publication helper atomically creates a fresh version tag
   at the approved source commit, then creates a draft with `--verify-tag`. An
   existing tag, even without a release, refuses the job before artifact upload.
   Directory submissions remain separate.

If draft creation or upload fails after tag reservation, the reserved tag remains.
The job never overwrites or deletes it automatically. A maintainer must inspect the
remote tag's exact commit and the existing draft/assets against the approved source
and receipt before a reviewed manual recovery. Use a new version or deliberately
complete that exact draft; an unchanged blind rerun will fail safely. Never move an
old release tag to make a rerun pass.

Local equivalent: `python3 scripts/release.py validate`,
`python3 -m unittest discover -s tests -v`, and
`python3 scripts/release.py build`. Build from a clean committed public tree.
Archives include only tracked files under `indaga/`, keep both host manifest
directories, and place the plugin at the archive root. Fixed file modes/timestamps
and uncompressed ZIP entries make artifact bytes reproducible across platforms.
The `.zip` and `.plugin` assets are identical; verify them with `SHA256SUMS`.
`release.json` ties file hashes to the public source commit.

The same build also emits four instruction-only standalone skill ZIPs. Each has
one namespaced skill folder, contained connection/evidence/contract references,
license and installation README. The build adapts only standalone names, local
links, upload-description length and connection-guide containment wording; it
records every transformation and file/archive hash in `release.json`. Standalone
packaging does not alter the complete plugin's canonical runtime instructions.
Existing draft-release ZIP selection includes these sidecar assets. See [optional-skill installation](optional-skills.md).
Packaging proof does not establish successful upload, host dependency behavior or
authenticated native acceptance for a standalone pack.

Schema checks use reviewed SHA-256 pins for the official portable schemas.
Host validation pins the Claude CLI version. Update those pins through a reviewed
PR when their upstream contracts change.

# Updating an installed plugin

Marketplace source updates do not prove that a running host loaded the new package.
Use the host's plugin update controls, then fully restart the host if its displayed
version or behavior stays old. In Claude Code, use `/plugin update indaga@indaga`
and start a fresh session. For Claude chat/Cowork and Codex, check the installed
plugin's version in its details, update/reinstall from the marketplace if needed,
and restart the application. Follow the host's current supported controls.

Confirm the installed version matches the released manifest, discover all four
skills, and establish a new connector sign-in if the hosted endpoint changed.
Do not copy an OAuth token from the old connection. The first workflow call must
confirm supported public-contract compatibility; old or local tools are a stop,
not permission to fall back. For QA, compare the installed manifest and skill file
hashes with `release.json`; a displayed catalogue version alone is insufficient.

Anthropic marketplace distribution and OpenAI directory uploads have separate
update paths. A GitHub release does not claim either directory approval or that an
already running host has refreshed its plugin cache.
