I haven't changed anything yet. There are two blockers, and I have no file-editing tool in this session, so the change below is for you to apply or approve.

**What I found in `.github/workflows/deploy.yml`:**

```yaml
on:
  pull_request:
permissions: write-all
jobs:
  deploy:
    steps:
      - uses: actions/checkout@v4
      - run: echo "Title is ${{ github.event.pull_request.title }}"
```

1. **The workflow has no build or test steps,** so there's nothing to upload "after the tests pass." The repo has Python code with tests (`src/ledger/`, `tests/test_balance.py`), Go code (`cmd/parser.go`) and a `Dockerfile`. I can't tell which one produces "the build artifact."
2. **Two security problems you should fix in the same change:**
   - **Line 14 lets anyone opening a PR run their own commands.** The PR title is pasted straight into the shell script, so a title like `` `curl …|sh` `` gets executed. Pass the title through `env:` and reference it as `"$PR_TITLE"` instead.
   - **Line 7 is too broad.** `permissions: write-all` on a `pull_request` trigger gives the job's token write access to the whole repo. Uploading an artifact needs no special token permission, so `contents: read` is enough.

**Proposed workflow,** assuming a Python package built with pytest and `python -m build`:

```yaml
---
name: deploy

on:
  pull_request:

permissions:
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: python -m pip install pytest build
      - name: Run tests
        run: python -m pytest tests/
      - name: Build
        run: python -m build
      - name: Upload build artifact
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: build-${{ github.sha }}
          path: dist/
          if-no-files-found: error
          retention-days: 7
      - name: Show PR title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: echo "Title is ${PR_TITLE}"
```

The steps run in order, so the upload only happens if the tests and build pass. `if-no-files-found: error` makes the job fail instead of quietly uploading nothing. For stronger supply-chain protection, pin the actions to full commit SHAs rather than version tags.

**To finish this, please tell me:**
- What the artifact is: a Python wheel, the Go binary from `cmd/`, or a Docker image.
- Whether to apply the edit once I have write access, or whether you'll paste it in yourself.
