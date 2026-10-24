I couldn't find an assistant workflow in this repository. The only workflow file is `.github/workflows/deploy.yml`. It doesn't run on PR comments (no `issue_comment` or `pull_request_review_comment` trigger), and it doesn't call any AI agent. So I couldn't check the agent's token, tools or network. The agent workflow may be in another repository, on a branch other than `main`, or not committed yet. If you tell me where it is, I'll review it.

`deploy.yml` does have problems of the same kind you asked about, so here they are.

**`.github/workflows/deploy.yml`**

1. **The token has far more access than the job needs** (`deploy.yml:7`). `permissions: write-all` gives write access to every scope at the workflow level. The job only checks out code and prints a line, so it needs nothing beyond `contents: read`. Set `permissions: {}` at the workflow level and add `contents: read` on the job.
2. **Script injection** (`deploy.yml:14`). `${{ github.event.pull_request.title }}` is pasted straight into the shell script. Anyone who opens a PR with a title like `"; curl … | sh #` can run commands while that write token is present. Pass the title through `env:` and print it with `printf '%s\n' "$PR_TITLE"`.
3. **The checkout credential stays on disk** (`deploy.yml:13`). Without `persist-credentials: false`, the token is left in `.git/config` for every later step.
4. **The action is referenced by a tag** (`deploy.yml:13`). `actions/checkout@v4` should be pinned to the full commit SHA of the current release, with the version in a comment. Tags can be moved to point at different code.
5. **No `timeout-minutes`.** The job can run for the 6-hour default.
6. **The name doesn't match what it does.** It's called `deploy` and runs on every `pull_request`, but it doesn't deploy anything. If a real deploy step is meant to go here, it shouldn't run on PR events.

For fork PRs, GitHub limits the `pull_request` token to read access, so findings 1 and 2 matter most for PRs opened from branches in this repository.

When you share the agent workflow, I'll check these points:
- Who can start it: a comment trigger needs a check on the commenter's association or permission.
- Which token the agent runs with, and its scopes.
- Its tool allowlist: no unrestricted shell.
- Whether its network access is limited.
- Whether the prompt includes PR or comment text an attacker controls.

I haven't changed any files or run `actionlint` or `zizmor`. I also couldn't open the skill's reference file on agent workflows because file access was denied, so these points come from the skill's main checklist. Do you want me to apply the fixes to `deploy.yml`?
