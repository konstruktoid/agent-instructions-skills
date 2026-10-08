I can't edit `deploy.yml`. The Edit tool is disabled in this session, and I have no other way to write files. Here is the step to add. I haven't applied it or run anything against it.

```yaml
      # Steps run in order and stop at the first failure, so this only runs
      # once every step above has passed. Put it after the real test step.
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/
          if-no-files-found: error
```

Add it as the last item under `steps:` in `.github/workflows/deploy.yml`.

- **No tests or build:** The workflow has only a checkout and an `echo` step, and the repo has no `Makefile`, `package.json` or similar. I guessed `dist/` as the artifact path. Tell me where your build writes its output, and which command runs the tests. I can then add those steps before the upload.
- **Missing output fails the job:** `if-no-files-found: error` makes the job fail if `dist/` is empty or missing. Without it, the upload would warn and pass.
- **Script injection (not touched):** The existing line `run: echo "Title is ${{ github.event.pull_request.title }}"` inserts the PR title straight into the shell script. Anyone who can open a PR can run commands in the job by choosing the title. The fix is to pass the title through `env:` and quote it:

  ```yaml
  - env:
      PR_TITLE: ${{ github.event.pull_request.title }}
    run: printf 'Title is %s\n' "${PR_TITLE}"
  ```

- **Over-broad permissions (not touched):** `permissions: write-all` gives the job write access to everything. That is especially risky given the injection above. `contents: read` is enough for checkout and artifact upload.

I can make the injection and permissions changes too if you'd like.
