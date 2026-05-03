#!/usr/bin/env python3
"""Generate a dark-code badge SVG.

For each `src/worstenbrood/**/*.py` file, counts lines added on `dark` vs the
current `HEAD` (`git diff HEAD..dark --numstat`, additions only). The dark
percentage is `additions / total_dark_lines`. Writes the result to
`docs/assets/dark-badge.svg`. Idempotent: only rewrites the SVG when the
content would change.

Run as a pre-commit hook. Skipped on `dark` (the diff would be empty against
itself; the badge tracks the gap between `dark` and the reviewed scope).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_PREFIX = "src/worstenbrood/"
SOURCE_SUFFIX = ".py"
BADGE_PATH = REPO_ROOT / "docs" / "assets" / "dark-badge.svg"


def lines_in_ref(ref: str) -> int:
    """Sum source-file line counts at the given git ref."""
    files = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    total = 0
    for path in files:
        if not path.startswith(SOURCE_PREFIX) or not path.endswith(SOURCE_SUFFIX):
            continue
        blob = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            check=True,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        ).stdout
        total += blob.count("\n")
    return total


def added_lines(base: str, head: str) -> int:
    """Sum source-file additions in `git diff base..head` (deletions ignored)."""
    out = subprocess.run(
        ["git", "diff", "--numstat", f"{base}..{head}"],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    ).stdout

    total = 0
    for line in out.splitlines():
        # `--numstat` format: "<added>\t<deleted>\t<path>". Binary files use "-".
        added, _, path = line.split("\t", 2)
        if added == "-":
            continue
        if not path.startswith(SOURCE_PREFIX) or not path.endswith(SOURCE_SUFFIX):
            continue
        total += int(added)
    return total


def render_svg(dark_percent: int) -> str:
    """Render a minimal flat-style dark-code badge."""
    if dark_percent <= 20:
        colour = "#44cc11"  # green
    elif dark_percent <= 50:
        colour = "#dfb317"  # yellow
    else:
        colour = "#e05d44"  # red

    label = "🌚 dark code"
    value = f"{dark_percent}%"

    label_w = 7 * len(label) + 10
    value_w = 7 * len(value) + 10
    total_w = label_w + value_w

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="20">'
        f'<linearGradient id="g" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>'
        f'<rect width="{total_w}" height="20" fill="#2a2a4e"/>'
        f'<rect x="{label_w}" width="{value_w}" height="20" fill="{colour}"/>'
        f'<rect width="{total_w}" height="20" fill="url(#g)"/>'
        f'<g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,sans-serif" font-size="11">'
        f'<text x="{label_w / 2}" y="14">{label}</text>'
        f'<text x="{label_w + value_w / 2}" y="14">{value}</text>'
        f"</g></svg>\n"
    )


def main() -> int:
    if not (REPO_ROOT / ".git").exists():
        print("badge.py: not a git repo, skipping", file=sys.stderr)
        return 0

    try:
        dark_lines = lines_in_ref("dark")
    except subprocess.CalledProcessError:
        print("badge.py: 'dark' ref not found, skipping", file=sys.stderr)
        return 0

    # Diff HEAD..dark, additions only. A modified line counts as 1 (the new
    # version is "dark"); a pure deletion contributes 0. HEAD rather than `main`
    # so feature branches off `main` count their content as reviewed.
    try:
        unreviewed_lines = added_lines("HEAD", "dark")
    except subprocess.CalledProcessError:
        print("badge.py: failed to diff HEAD..dark, skipping", file=sys.stderr)
        return 0

    dark_percent = (
        0 if dark_lines == 0 else min(100, round(100 * unreviewed_lines / dark_lines))
    )
    new_svg = render_svg(dark_percent)

    BADGE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if BADGE_PATH.exists() and BADGE_PATH.read_text() == new_svg:
        return 0  # no change

    BADGE_PATH.write_text(new_svg)
    print(f"badge.py: wrote {BADGE_PATH.relative_to(REPO_ROOT)} ({dark_percent}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
