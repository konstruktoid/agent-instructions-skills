I rewrote `.github/workflows/assistant.yml`. The workflow is not safe to turn on yet: `acme/coding-agent` is still unpinned, and none of it has run. I haven't committed anything.

## What was wrong
1. **`permissions: write-all`** gave every job every scope.
2. **Anyone could trigger it.** Any commenter on a public repo could start it, including on issues, and edits re-triggered it. The agent held your model key and a write token, and it took the comment text as its instructions.
3. **The checkout used a moving ref.** `refs/pull/N/head` can change between the comment and the checkout. It also checked out fork code into a job holding secrets, and left the token in `.git/config`.
4. **Unpinned and stale actions.** `checkout@v5` was a mutable tag and `acme/coding-agent@v1` still is.
5. **No `timeout-minutes`, no `concurrency`.** The default timeout is 360 minutes.

## What I changed
- **Permissions:** `permissions: {}` at workflow level, with scopes set per job.
- **Trigger:** `types: [created]` only, and only on pull request comments.
- **Two jobs, so the gate runs before the agent:**
  - `authorize` has read-only scopes and rejects bot commenters. Association alone isn't a permission check, so it also looks up the commenter's role and requires write, maintain or admin. It resolves the PR head to a commit SHA and refuses fork PRs.
  - `assistant` checks out that SHA, and its scopes are `contents: write` and `pull-requests: write`. It has no `id-token` or `actions` scope, and `persist-credentials: false` is set.
- **Agent config:** before the agent runs, the job deletes `CLAUDE.md`, `AGENTS.md`, `.mcp.json` and `.claude/` from the checkout, so the PR can't supply them.
- **Comment text:** it reaches the agent only as an action input, and the prompt says it is data. This doesn't remove prompt injection. The gate, the token scope and the environment approval are what contain that risk.
- **Pinning and limits:** `checkout` is pinned to the SHA for v7.0.1, which I looked up. It was released 2026-07-20 and is the latest release. The jobs have timeouts of 5 and 30 minutes. Concurrency is one run per PR, with no cancel-in-progress so a push isn't cut off midway.
- **Model key:** the agent job uses `environment: assistant` so the key can sit behind required reviewers.

## Verification
- `actionlint` passes.
- `zizmor` (offline, pedantic) leaves two findings in `assistant.yml`:
  - **`dangerous-triggers`** is the `issue_comment` trigger itself. It is intended and mitigated by the gates above. I didn't add a suppression.
  - **`unpinned-uses`** is `acme/coding-agent@v1`. The GitHub API returns 404 for that repo, so I couldn't resolve a SHA and didn't invent one. Pin it to a reviewed release SHA before enabling.
- The online zizmor audit fails for the same reason, because `acme/coding-agent` doesn't resolve.
- **Not run:** I didn't push or trigger the workflow, so the whole thing is unverified at runtime. The collaborator-permission lookup is the part most likely to need adjusting. If it returns 403 with the default token, the `authorize` job needs a GitHub App token.

## What you need to do
- Create an `assistant` environment with required reviewers, and move `MODEL_API_KEY` into it.
- Check how the agent pushes. It now gets only `GH_TOKEN` and no stored git credential. If the action expects git to be pre-authenticated, it needs a setup step.
- Add a `CODEOWNERS` file covering `.github/` and any scripts a workflow runs. None exists.
- Set a branch ruleset so the push can't reach protected branches. It then lands only on the PR branch.
- Set "require approval for outside collaborators" in the repository's Actions settings.
- `ci.yml` is outside what you asked for. It has low-severity findings (job name, concurrency) and pins `checkout` at v5.0.0, which is behind v7.0.1. I left it alone.
