I couldn't make the edit because this session doesn't give me a file-editing tool. Here's the change to apply to `.github/workflows/deploy.yml`.

**Current state** (`.github/workflows/deploy.yml:7`): `permissions: write-all` gives the job's GitHub token write access to every scope. The job only checks out the code and echoes a line, so the one permission it needs is read access to the repository contents.

**Proposed file:**

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

**What changed and why:**
- **`permissions: {}` at the top level:** any job added later starts with no permissions and has to declare what it needs.
- **`contents: read` on the job:** this is the only permission `actions/checkout` needs here.
- **`persist-credentials: false`:** stops checkout from leaving the token in `.git/config`, where later steps could read it.

**I also changed one line you didn't ask about, because the job can be attacked through it:** line 14 puts `${{ github.event.pull_request.title }}` straight into the shell command. Whoever opens the PR controls the title, so a title like `` `curl …|sh` `` would run as code. With `write-all`, that code would have had a write-capable token. Passing the title in through an `env:` variable makes the shell treat it as plain text.

**Worth doing next:**
- Pin `actions/checkout` to a full commit SHA instead of `@v4`.
- Your branch is about imposter commits, so also check that the SHA you pin is actually in `actions/checkout`'s own history.
- A workflow named "deploy" that runs on `pull_request` is unusual. If it's meant to deploy, it should probably run on `push` to the main branch or through a protected `environment:`, so that PR code can't reach deployment credentials.

If you'd rather require restricted token permissions for every repo in the organization, set the organization's default workflow permissions to read-only.
