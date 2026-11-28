I couldn't make this change. In this session I can only read files: I have no tool to edit a file and no shell or network access to look up commit SHAs. I'm also not going to write a SHA from memory, because a wrong one either breaks the workflow or points at code nobody reviewed.

**What's in the repo:** one workflow, `.github/workflows/deploy.yml`, which uses one action at line 13: `actions/checkout@v4`.

**To get the SHA,** look up the current release, then the commit it points to:

```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name          # e.g. vX.Y.Z
gh api repos/actions/checkout/commits/refs/tags/<that-tag> --jq .sha  # 40-char SHA
```

Pin to the latest release rather than whatever `v4` points to now, and read its release notes, since it may be a major-version jump from v4. Alternatively, `pinact run` or `ratchet pin` rewrites every `uses:` line to a SHA and keeps a version comment.

**This file has more serious problems than the tag.** It runs on `pull_request` and:

1. **Line 14 lets a PR title run as code.** `${{ github.event.pull_request.title }}` is pasted into the shell script before it runs, so a crafted title executes on the runner.
2. **Line 7 gives the job full write access** (`permissions: write-all`). A job like this only needs `contents: read`.
3. **There's no job timeout,** and checkout leaves its token in `.git/config` for later steps.

Here's the version I'd put in place, with the SHA left for you to fill in:

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
      - uses: actions/checkout@<40-char-sha> # <release tag>
        with:
          persist-credentials: false
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
```

Nothing has been checked: no `actionlint`, no `zizmor`, no test run. After filling in the SHA, run `actionlint` and `uvx zizmor@1.31.1 --persona=pedantic .` on it. If you give me edit and shell access, I can do the lookup, the edit and the checks myself.
