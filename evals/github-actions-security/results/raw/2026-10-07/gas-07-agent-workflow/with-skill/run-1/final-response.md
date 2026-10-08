I hardened `.github/workflows/assistant.yml`, but one thing is still open: `acme/coding-agent@v1` is not pinned to a commit SHA. `actionlint` is clean. `zizmor` (offline, pedantic) reports one high finding, `unpinned-uses`, on that line, plus two suppressed findings that I didn't inspect. Nothing has been run on a real runner, and I didn't commit or push.

**Do this before enabling it.** Pin `acme/coding-agent` to a full commit SHA. I couldn't look up a release for it (the GitHub API returned 404 from here), and I didn't want to invent a SHA. A `TODO` comment marks the spot.

**What I changed and why**
- **Permissions.** The workflow had `write-all`, so every scope was granted to a job that runs an agent. It is now `permissions: {}` at workflow level. The one job gets only `contents: write` (the agent has to push) and `pull-requests: write`, each with a comment saying why.
- **Who can trigger it.** Previously any commenter on any issue or PR could start a run that held `MODEL_API_KEY` and a write token.
  - The job now only runs for pull request comments from an OWNER, MEMBER or COLLABORATOR.
  - A first step then checks the commenter's real role through the API and requires write, maintain or admin, because those association labels don't prove write access.
- **Edited comments.** The trigger is now `created` only. Before, editing an old comment re-ran the agent.
- **Fork PRs.** The old `refs/pull/N/head` checkout pulled in fork code alongside the secrets. The workflow now refuses fork PRs. That means fork PRs no longer work; the agent could not push to a fork with this token anyway.
- **Checkout.** It now uses the exact head commit SHA captured when the comment was authorized, so the branch can't change between the comment and the checkout. `actions/checkout` is pinned to v7.0.1, the latest release (`3d3c42e5…`), where it was previously the mutable `@v5`.
- **Agent configuration.** A step deletes `.mcp.json`, `.claude/`, `CLAUDE.md` and `AGENTS.md` from the checkout, because the PR branch could otherwise supply tools, hooks or instructions to the agent.
- **Credentials.** `persist-credentials: true` is deliberate, since the agent pushes. I noted that in the workflow.
- **Prompt.** The comment body now goes in as a delimited input labelled as data. It is not interpolated into any `run:` script. This reduces prompt injection but doesn't remove it. What contains it is the token scope and the gates above.
- **Limits.** Added a 15-minute timeout (the default is 360) and per-PR concurrency that queues runs instead of cancelling one mid-push.

**Still worth doing**
- **Agent tool allowlist.** If `acme/coding-agent` supports one, set it to named commands rather than a general shell.
- **Model-key environment.** Put `MODEL_API_KEY` in an environment with required reviewers.
- **Egress restriction.** Restrict outbound network access for the job.
- **Branch protection.** Make sure rulesets protect the default branch, so the agent can only push to PR branches.
- **CODEOWNERS.** Cover `.github/workflows/`, the `Makefile` and any scripts a workflow runs. `GITHUB_TOKEN` can't edit workflow files, but the agent can still change what the next run executes.
- **`ci.yml`.** It is pinned to checkout v5.0.0, not the latest release. I left it alone because it is out of scope.
