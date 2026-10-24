I haven't changed anything yet. This session has no tool that can edit files or run commands, and I won't pin to a SHA I haven't looked up, because a SHA from memory could point at the wrong commit or not exist.

**What needs pinning:** the repo has one action reference: `actions/checkout@v4` at `.github/workflows/deploy.yml:13`. Run these two commands to get the current release and its commit SHA:

```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name   # e.g. vX.Y.Z
gh api repos/actions/checkout/commits/<that-tag> --jq .sha     # 40-char SHA
```

Then change line 13 to:

```yaml
      - uses: actions/checkout@<40-char-sha> # <tag>
```

This should pin the newest release, not just the commit behind `v4`. If that's a new major version (v5 or later), check its release notes for breaking changes before merging.

**Two more serious problems in the same 15-line file.** Pinning won't help much while these remain:

1. **`permissions: write-all` (line 7)** gives every job write access to the repository on every pull request. The job only checks out code and echoes, so set `permissions: {}` at the top and give the job `contents: read`.
2. **Script injection (line 14).** The PR title is pasted directly into the shell command. Anyone who can open a PR can choose a title that runs their own commands, and with `write-all` those commands get a token that can write to the repo. Pass the title through `env:` instead.

This is the whole file with all fixes applied; only the SHA line still needs filling in:

```yaml
---
name: deploy

on:
  pull_request:

permissions: {}

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@<resolved-sha> # <resolved-tag>
        with:
          persist-credentials: false
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
```

The other additions are `timeout-minutes: 10`, so a stuck job can't run for the 6-hour default, and `persist-credentials: false`, which keeps the token out of `.git/config`.

After the edit, check it with:

```sh
docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint@sha256:b1934ee5f1c509618f2508e6eb47ee0d3520686341fec936f3b79331f9315667 -color
uvx "zizmor@1.31.1" --persona=pedantic .
```

If you give me edit and shell access, I can look up the SHA, apply all of this and run both checks myself.
