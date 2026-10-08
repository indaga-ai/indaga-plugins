#!/usr/bin/env bash
# Final publication boundary, after package, hosted and native acceptance checks.
set -euo pipefail
: "${RELEASE_VERSION:?}" "${GITHUB_SHA:?}" "${GITHUB_REPOSITORY:?}"
[[ "$RELEASE_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]
[[ "$GITHUB_SHA" =~ ^[0-9a-f]{40}$ ]]

# Create, never update: GitHub refuses an existing tag, including a tag with no release.
# This reserves the approved source atomically; --target alone would reuse an old tag.
gh api --method POST "repos/$GITHUB_REPOSITORY/git/refs" \
  -f "ref=refs/tags/v$RELEASE_VERSION" -f "sha=$GITHUB_SHA" --silent

gh release create "v$RELEASE_VERSION" \
  dist/indaga-*.zip dist/indaga-*.plugin dist/SHA256SUMS dist/release.json \
  --repo "$GITHUB_REPOSITORY" \
  --draft --verify-tag --title "Indaga $RELEASE_VERSION" \
  --notes-file docs/release-notes.md
