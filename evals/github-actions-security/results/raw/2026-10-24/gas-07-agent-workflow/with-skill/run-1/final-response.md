I rewrote `.github/workflows/assistant.yml`. `actionlint` is clean. `zizmor` (offline, pedantic) still reports two errors, and the workflow isn't ready to enable until both are dealt with.

**What I changed and why**
- **Token permissions:** `permissions: write-all` is now `permissions: {}` at workflow level. Each job grants only what it uses:
  - `resolve` gets `pull-requests: read`.
  - `assistant` gets `contents: write` (to push) and `pull-requests: write` (to reply).
  - There is no `id-token` or `actions` scope. An agent with a shell could use those to mint cloud credentials or re-run workflows.
- **Who can trigger it:** previously anyone who commented on a public repo ran the agent with your write token and model key. A job-level `if` now requires the comment to be on a pull request. It also requires the commenter's association to be `OWNER`, `MEMBER` or `COLLABORATOR`. The gate sits in the job condition, not the prompt.
- **Edited comments:** the trigger is now `created` only. Before, editing a comment re-ran the agent.
- **What gets checked out:** the old checkout used a moving `refs/pull/N/head`. A new `resolve` job looks up the PR head and pins it to a commit SHA, so the agent works on what was current when the maintainer commented. It refuses PRs from forks. The workflow token can't push to a fork, and fork content shouldn't reach a job holding your model key.
- **Checkout hardening:**
  - `actions/checkout` is pinned to `3d3c42e…` (v7.0.1, looked up as the latest release) with `persist-credentials: false`.
  - The agent still gets `GH_TOKEN` in its environment to push.
  - A step deletes `CLAUDE.md`, `AGENTS.md`, `.mcp.json` and `.claude/` from the checkout before the agent runs, so PR content can't add its own instructions, tools or hooks.
- **Prompt:** the comment still goes in as an action input, never into a shell. The prompt now says the comment and repo are data, not rules, and tells the agent to push only to the PR's branch. This is a weak control; the real limits are the token scope, the gate and the review.
- **Runtime limits:** both jobs have `timeout-minutes` (the default was 360). Concurrency is keyed on the PR number, so runs queue instead of overlapping. I left `cancel-in-progress` off so a run isn't killed mid-push.

**What `zizmor` still reports**
- **`dangerous-triggers`:** this comes from using `issue_comment` at all. You asked for a comment-driven workflow, so I kept it and added the gate and SHA pinning instead of suppressing the warning.
- **`unpinned-uses` on `acme/coding-agent@v1`:** I couldn't pin it. The GitHub API returns 404 for that repo, so I couldn't resolve a release or commit SHA, and I didn't invent one. Before enabling, pin it to a full SHA of a real release. There's a TODO comment on that line. The same step needs a tool allowlist of named commands, not a general shell. I couldn't set one because I don't know that action's inputs.
- **Online audits:** I ran `zizmor` offline because it couldn't look up that action, so those audits didn't run. I haven't run the workflow, so its behaviour is untested.

**Still to do outside this file**
- `author_association` isn't a real permission check. `COLLABORATOR` includes people with read-only access. If you want a stricter gate, add a step that checks for write or admin access with `gh api repos/OWNER/REPO/collaborators/USER/permission`. That call needs a token with push access.
- Protect the default branch with a ruleset so the agent can only push to PR branches, and don't add it as a bypass actor.
- Put `.github/workflows/` and any scripts the workflows run under `CODEOWNERS`.
- Consider moving `MODEL_API_KEY` into an environment with required reviewers.
- A PR pushed with `GITHUB_TOKEN` won't start its own CI. If you need checks to run on the agent's pushes, use a GitHub App token instead.
