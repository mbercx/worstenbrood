[![Templated from python-copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/mbercx/python-copier/refs/heads/main/docs/img/badge.json)](https://github.com/mbercx/python-copier)

# `worstenbrood`

![dark code badge](docs/assets/dark-badge.svg)

> ⚠️ **This package is LLM-assisted.** All code on `main` has been written or reviewed by a human. Unreviewed agent work lives on the `dark` branch and reaches `main` only after human review.

The `worstenbrood` Python package.

## Trying out the dark branch

`pip install` from PyPI gives you only reviewed code, which currently isn't much. To live on the `dark` edge:

```bash
pip install git+https://github.com/mbercx/worstenbrood.git@dark
```

This installs whatever is currently on `dark` — agent-written, not yet human-reviewed. Use at your own peril; reports of broken outputs welcome at [github.com/mbercx/worstenbrood/issues](https://github.com/mbercx/worstenbrood/issues).

## For contributors

Two long-lived branches:

- `main` — pristine reviewed history. Every commit is human-authored or human-reviewed line-by-line. PyPI releases come from here.
- `dark` — agent work piled on top of `main`. Force-pushed when rebuilt; never released to PyPI.

### Exploring the darkness

Add to `~/.gitconfig` (or `<repo>/.git/config`):

```ini
[alias]
    dark-explore = !git merge --squash dark && git reset && rm -f "$(git rev-parse --git-dir)/SQUASH_MSG"
```

`dark-explore` brings dark's content into the working tree (unstaged) without committing or polluting the squash-message buffer:

```bash
git checkout main
git checkout -b review/<feature>
git dark-explore                # working tree = dark, index clean
```

Review what you are interested in, and make changes as you like.
Stage the changes you are ready to give your stamp of approval, commit, and open a PR.

After committing your reviewed subset, the working tree still contains every other dark change as unstaged dirt.
`git stash` (or `git checkout -- .`) before moving on, otherwise those leftovers will follow you to the next branch.

### Other changes

Any other changes you would like to make can be done via a PR to `main` as usual.

## For maintainers

Once a contributor's PR (or your own promotion commit) lands on `main`, rebuild the `dark` branch with the provided script:

```ini
[alias]
    dark-rebuild = !./dev/dark/rebuild.sh
```

```bash
git checkout main
git dark-rebuild                # local-only; runs ./dev/dark/rebuild.sh
git push origin main            # skip if `main` is already in sync with remote
git push --force-with-lease origin dark
```

If the working tree is dirty (you just promoted with `dark-explore` and committed a subset), the leftover becomes a single `🌚 Dark code` commit on top of the new `main`, which is added to `dark`.
If the working tree is clean (you committed directly on `main`, or already pulled a contributor's merge), `dark-rebuild` simply rebases `dark` on your local `main`.
