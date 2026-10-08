I couldn't add the upload step. This session has no tool for editing files, so `.github/workflows/deploy.yml` is unchanged.

Here is the step I'd add to the end of the `steps:` list:

```yaml
      # Steps run in order and a failed step skips the rest, so this runs only
      # after the preceding steps (tests) have passed.
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/
          if-no-files-found: error
```

Three problems in the current workflow affect this:

- **No tests or build exist yet.** The only steps are a checkout and an `echo`. I found no `Makefile`, `package.json`, `pyproject.toml`, `go.mod` or `Cargo.toml` to take commands from. You'll need to add the test and build steps before the upload. `dist/` is a guess, so change it to wherever your build writes its output. `if-no-files-found: error` makes the upload fail if that directory is empty.
- **The `echo` step is injectable.** `echo "Title is ${{ github.event.pull_request.title }}"` pastes the PR title straight into the shell script. Anyone who can open a PR can run commands in the job. The fix is to pass the title through `env:` and echo `"$PR_TITLE"` instead.
- **The token is over-privileged.** `permissions: write-all` combined with the injection above is risky. Uploading artifacts needs no extra token permissions, so `contents: read` is enough.

I haven't changed either of the last two. If you give me edit access, or tell me to go ahead, I can apply all three, once I know your build and test commands and the artifact path.
