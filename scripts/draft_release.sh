#!/usr/bin/env bash
# Final publication boundary, after package, hosted and native acceptance checks.
set -euo pipefail
: "${RELEASE_VERSION:?}" "${GITHUB_SHA:?}" "${GITHUB_REPOSITORY:?}"
[[ "$RELEASE_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]
[[ "$GITHUB_SHA" =~ ^[0-9a-f]{40}$ ]]

# Create, never update: each existing tag refuses before any artifact upload.
# Claude dependency constraints resolve the per-plugin tags, not just the release tag.
# Reservation is atomic per reference; a later collision leaves earlier tags reserved.
for release_tag in "v$RELEASE_VERSION" "indaga--v$RELEASE_VERSION" "indaga-weekly--v$RELEASE_VERSION"; do
  gh api --method POST "repos/$GITHUB_REPOSITORY/git/refs" \
    -f "ref=refs/tags/$release_tag" -f "sha=$GITHUB_SHA" --silent
done

gh release create "v$RELEASE_VERSION" \
  dist/indaga-*.zip dist/indaga-*.plugin dist/SHA256SUMS dist/release.json \
  --repo "$GITHUB_REPOSITORY" \
  --draft --verify-tag --title "Indaga $RELEASE_VERSION" \
  --notes-file docs/release-notes.md
