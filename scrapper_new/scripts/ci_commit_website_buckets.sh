#!/usr/bin/env bash
# Stage scrapper_new feed JSON + scrape_meta under website/public/data/, commit if changed, push.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

DATA_DIR="website/public/data"
FEEDS=(
  news.json
  results.json
  jobs.json
  syllabus.json
  admit_cards.json
  enrollments.json
  blogs.json
)

files=()
for f in "${FEEDS[@]}"; do
  p="${DATA_DIR}/${f}"
  if [[ -f "$p" ]]; then
    files+=("$p")
  fi
done
if [[ -f "${DATA_DIR}/scrape_meta.json" ]]; then
  files+=("${DATA_DIR}/scrape_meta.json")
fi

if [[ "${#files[@]}" -eq 0 ]]; then
  echo "No scrapper_new data files under $DATA_DIR — skipping commit"
  exit 0
fi

git add -- "${files[@]}"

if git diff --staged --quiet; then
  echo "No changes to scrapper_new feed data or scrape_meta — skipping commit"
  exit 0
fi

echo "---- Staged changes (stat) ----"
git diff --staged --stat
echo "---- Staged files ----"
git diff --staged --name-only

git commit -m "chore: update feed data from scrapper_new"

BRANCH="${GITHUB_REF_NAME:-$(git rev-parse --abbrev-ref HEAD)}"
git fetch origin "$BRANCH"

SAFE_REGEX='^website/public/data/(news|results|jobs|syllabus|admit_cards|enrollments|blogs|scrape_meta)\.json$'
if ! git merge "origin/${BRANCH}" -m "Merge origin/${BRANCH} before push (scrapper_new)"; then
  OUTSIDE=$(git diff --name-only --diff-filter=U | grep -vE "${SAFE_REGEX}" || true)
  if [[ -n "$OUTSIDE" ]]; then
    echo "Merge conflict outside scrapper_new paths — resolve manually:"
    echo "$OUTSIDE"
    git merge --abort
    exit 1
  fi
  git checkout --ours -- \
    "${DATA_DIR}/news.json" \
    "${DATA_DIR}/results.json" \
    "${DATA_DIR}/jobs.json" \
    "${DATA_DIR}/syllabus.json" \
    "${DATA_DIR}/admit_cards.json" \
    "${DATA_DIR}/enrollments.json" \
    "${DATA_DIR}/blogs.json" \
    "${DATA_DIR}/scrape_meta.json"
  git add -- \
    "${DATA_DIR}/news.json" \
    "${DATA_DIR}/results.json" \
    "${DATA_DIR}/jobs.json" \
    "${DATA_DIR}/syllabus.json" \
    "${DATA_DIR}/admit_cards.json" \
    "${DATA_DIR}/enrollments.json" \
    "${DATA_DIR}/blogs.json" \
    "${DATA_DIR}/scrape_meta.json"
  GIT_EDITOR=true git commit --no-edit
fi

git push origin "$BRANCH"

echo "Committed and pushed scrapper_new feed data + scrape_meta."
