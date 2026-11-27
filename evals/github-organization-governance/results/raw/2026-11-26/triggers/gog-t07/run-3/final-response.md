I can't edit files in this session (I only have read and search tools here), so below is the change for you to apply. I haven't changed or tested anything.

**Current state** (`.github/workflows/deploy.yml:7`): `permissions: write-all` gives the `GITHUB_TOKEN` write access to every scope. The job only checks out code and echoes a string, so it only needs `contents: read`.

**Proposed change:** remove all permissions at the workflow level, then grant the job only what it uses:

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
      - run: echo "Title is ${{ github.event.pull_request.title }}"
```

- With `permissions: {}` at the top, any job added later starts with no access and has to ask for what it needs.
- `contents: read` is all `actions/checkout` needs.
- `persist-credentials: false` stops checkout from leaving the token in `.git/config`, where later steps could read it. Nothing in this job pushes, so it doesn't need the token.

If the real deploy steps need more, add only those scopes to the `deploy` job. For example, cloud OIDC login needs `id-token: write`, and creating a deployment record needs `deployments: write`.

**Two other problems in this file:**

1. **Script injection at line 14.** The PR title is inserted straight into the shell command, so whoever opens the PR can run commands in the job. Before the fix, those commands would run with a write-all token. Pass the title through an environment variable instead:
   ```yaml
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: echo "Title is ${PR_TITLE}"
   ```
2. **`actions/checkout@v4` uses a tag that can be moved to different code.** Pin it to the full commit SHA, with the tag in a comment.

Also, a workflow named "deploy" that runs on `pull_request` will run code from unreviewed PRs. If it's meant to actually deploy, it should run on `push` to the main branch or on `workflow_dispatch`, behind a protected environment.
