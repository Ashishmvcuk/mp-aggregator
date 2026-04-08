#!/usr/bin/env bash
# Stage only category JSON under website/public/data/, show diff, commit if needed, push.
# Run from repo root. Does nothing if no *.json changed — live site on GitHub stays unchanged.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

shopt -s nullglob
files=(website/public/data/*.json)

if [ "${#files[@]}" -eq 0 ]; then
  echo "No JSON files under website/public/data — skipping commit"
  exit 0
fi

git add -- "${files[@]}"

if git diff --staged --quiet; then
  echo "No changes to website/public/data/*.json — skipping commit (live site data unchanged on main)"
  exit 0
fi

echo "---- Staged changes (stat) ----"
git diff --staged --stat
echo "---- Staged files ----"
git diff --staged --name-only

git commit -m "chore: update scraped website data"

# Remote main may have moved (deploys, other commits). Rebase our commit on top, then push.
BRANCH="${GITHUB_REF_NAME:-$(git rev-parse --abbrev-ref HEAD)}"
git fetch origin "$BRANCH"
if ! git rebase "origin/${BRANCH}"; then
  echo "Rebase onto origin/${BRANCH} failed (likely overlapping edits). Resolve on a clone or merge main locally, then rerun."
  exit 1
fi

git push origin "$BRANCH"

echo "Committed and pushed updated website data."
