I hardened `.github/workflows/assistant.yml`, but it isn't ready to turn on yet. `acme/coding-agent` is still pinned only to the `v1` tag. I couldn't look it up through the GitHub API (it returned 404 for me), so I had no real commit SHA to pin. Pin it to a full commit SHA before you enable the workflow.

**What was wrong**
- **No actor gate.** Anyone who could comment on a public repo could start a run with the repo token and your model API key. The gate is now an `if` on the job, restricted to pull request comments from `OWNER`, `MEMBER` or `COLLABORATOR`.
- **Association isn't permission.** A `COLLABORATOR` can have read-only access. The first step now calls the collaborators API and requires `admin`, `maintain` or `write` before anything else runs.
- **`permissions: write-all`.** The workflow default is now `permissions: {}`. The job gets only `contents: write` (to push) and `pull-requests: write` (to comment).
- **Unpinned branch checkout.** It used `refs/pull/N/head`, and for issue comments that expression produced garbage. The gate step now resolves the PR head to a commit SHA and checks out that exact commit.
- **Fork PRs.** The workflow now refuses them. Fork code could carry agent config files and prompt-injection text, and the repo token can't push to a fork anyway.
- **Edited comments.** The trigger is now `created` only, so editing a comment can't start a second run.
- **Checkout token.** Checkout now sets `persist-credentials: false`, so the token isn't left in `.git/config`.
- **Agent config in the checkout.** A new step deletes `CLAUDE.md`, `AGENTS.md`, `.mcp.json` and `.claude/` before the agent runs.
- **Pinning.** `actions/checkout` is pinned to `3d3c42e5…` (v7.0.1, the current release I looked up).
- **Runtime and prompt.** There was no timeout, so I set `timeout-minutes: 30`. The prompt now labels the comment as untrusted text. That is a mitigation only, not a boundary.
- **Concurrency.** There is now one run per PR, and runs aren't cancelled mid-push.

I kept the behaviour: a maintainer comments, the agent edits the code and pushes to the PR branch.

**Checks**
- `actionlint` is clean.
- `zizmor` with `--persona=pedantic --offline` leaves two findings in this file. One is the unpinned `acme/coding-agent@v1`. The other is the `issue_comment` trigger, which zizmor always flags, and the actor gate and permission check are my answer to it. I added no suppressions.
- The online `zizmor` run crashes because it can't resolve the `acme/coding-agent` repo, so I used `--offline`.
- I did not run the workflow, so none of the new behaviour has been exercised on a runner. A real test would be a maintainer comment on a same-repo PR, plus a comment from a read-only collaborator that should be refused.

**Still open**
- **Agent tools.** I don't know which inputs `acme/coding-agent` accepts, so I couldn't set a tool allowlist. If it has one, name the permitted commands and don't grant a general shell.
- **Push token.** The agent step still holds `GITHUB_TOKEN` and `MODEL_API_KEY` so it can push. Put the key in an environment with required reviewers if you want an approval step.
- **Branch rules.** The token can't push to a protected branch, so keep branch protection on `main`. Don't add the bot as a bypass actor, and require a code owner on any path a workflow executes.
- **Public logs.** The agent's output goes to a public job log, so don't have it print secrets.
- **ci.yml.** `ci.yml` has unrelated pedantic findings (no job name, no concurrency). I left it alone.
