I didn't add the step, for two reasons:

1. **There are no tests or build to hook it onto.** `.github/workflows/deploy.yml` has a single job with two steps: a checkout, and a `run:` step that echoes the PR title. Nothing produces a build artifact and nothing runs tests, so "after the tests pass" has no step to follow, and there's no file path to upload.
2. **I can't edit files in this session.** I only have read and search tools here, so I can't write to the workflow.

**Two security problems in the current workflow** (`.github/workflows/deploy.yml`), which you should fix in the same change:
- **Line 7, `permissions: write-all`:** this runs on `pull_request`, so every PR gets a token that can write everything. Scope it down, for example to `permissions: contents: read`.
- **Line 14, `${{ github.event.pull_request.title }}` inside `run:`:** this is a script injection. Whoever opens the PR controls the title, and it gets pasted straight into the shell script. Pass it through an environment variable instead:
  ```yaml
  - env:
      PR_TITLE: ${{ github.event.pull_request.title }}
    run: printf 'Title is %s\n' "$PR_TITLE"
  ```

**Here's roughly what the step would look like** once a build and test step exist:
```yaml
      - name: Build
        run: <your build command>
      - name: Test
        run: <your test command>
      - name: Upload build artifact
        if: success()
        uses: actions/upload-artifact@v4   # ideally pinned to a full commit SHA
        with:
          name: build
          path: <build output dir, e.g. dist/>
          if-no-files-found: error
          retention-days: 7
```

Steps already stop at the first failure, so placing the upload after the tests is enough. `if: success()` just makes that explicit.

If you tell me the build and test commands and where the output goes, or confirm this is the right workflow file, I can give you the exact final YAML. You'd need to apply it yourself or run me with edit permissions.
