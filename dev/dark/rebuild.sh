#!/usr/bin/env bash
# Rebuild `dark` to sit cleanly on top of `main`.
#
# Two scenarios:
#   1. Promotion: working tree on `main` is dirty (full pre-promotion `dark` content
#      minus the just-committed reviewed subset). Carry the leftover to `dark` via
#      stash, commit as a single 🌚 commit.
#   2. Direct edit: working tree on `main` is clean. Rebase `dark` on `main`.
#
# Local-only; never pushes. User pushes both branches manually.
#
# Refuses to run unless current branch is `main` (avoids accidental invocation
# from `dark` or a feature branch).

set -euo pipefail

CURRENT=$(git symbolic-ref --short HEAD)
if [[ "$CURRENT" != "main" ]]; then
    echo "error: dark-rebuild must run on 'main' (current: '$CURRENT')" >&2
    exit 1
fi

if ! git rev-parse --verify --quiet dark > /dev/null; then
    echo "error: 'dark' branch does not exist" >&2
    exit 1
fi

# Scenario 2: clean working tree (direct human edit on main).
if git diff --quiet HEAD; then
    echo "Working tree clean — rebasing dark on main."
    git checkout dark
    git rebase main
    echo "Done. Push when ready: git push --force-with-lease origin dark"
    exit 0
fi

# Scenario 1: dirty working tree (promotion leftover).
echo "Working tree dirty — carrying leftover to dark via stash."

git stash push --include-untracked --message dark-leftover

# Verify stash actually captured something (defensive).
if ! git stash list | grep -q dark-leftover; then
    echo "error: stash push did not produce a dark-leftover entry" >&2
    exit 1
fi

git checkout dark
git reset --hard main

# Pop the stash. By construction this cannot conflict (same base tree).
if ! git stash pop; then
    echo "error: stash pop failed unexpectedly" >&2
    echo "       inspect with: git stash list && git status" >&2
    exit 1
fi

git add -A
git commit -m "🌚 Dark code"
echo "Done. Push when ready:"
echo "  git push origin main"
echo "  git push --force-with-lease origin dark"
