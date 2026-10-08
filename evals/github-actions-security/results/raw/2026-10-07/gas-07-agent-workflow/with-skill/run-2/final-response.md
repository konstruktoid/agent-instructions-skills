I rewrote `.github/workflows/assistant.yml`. It still isn't safe to turn on, because I couldn't pin the agent action. Where it stands:

- **actionlint:** clean.
- **zizmor, offline:** one real finding left, `unpinned-uses` on `acme/coding-agent@v1`. Offline coverage is reduced and online audits were skipped. The other findings are informational (`anonymous-definition`, and `concurrency-limits` on `ci.yml`). I left `ci.yml` alone.
- **Not run:** the workflow itself. It needs a real PR comment from a maintainer, and pushing the file to a branch or triggering it were outside what you asked for. The behaviour is unverified until it runs.

## What was wrong
The original combination was dangerous on a public repo:
- **Anyone could start it.** `issue_comment` fires for any commenter, and there was no check on who. Any passerby could comment and get an agent with a write token and your model key to act on their text.
- **Token was too wide.** `permissions: write-all` gave that agent every scope, including `actions`, `id-token` and `packages`.
- **Edits re-triggered it.** The `edited` trigger meant a comment could be changed after approval and fire again.
- **Fork code was exposed to the secrets.** It checked out `refs/pull/N/head` with no fork check, so fork-controlled files, including `CLAUDE.md` and `.mcp.json`, sat next to the secrets.

## What I changed
- **Trigger:** `created` only, and only on pull request comments.
- **Actor gate:** a job-level `if` requires an OWNER, MEMBER or COLLABORATOR association. The first step then calls the collaborators API and requires `write`, `maintain` or `admin`, because association alone includes read-only invitees.
- **Permissions:** `permissions: {}` at workflow level. The job gets `contents: write` (to push) and `pull-requests: read`, nothing else.
- **Fork PRs refused:** the workflow fails on fork PRs. Your token couldn't push to a fork anyway, and this keeps untrusted code away from the model key.
- **Pinned head:** the PR head is resolved to a commit SHA and that SHA is checked out. The head branch name goes to the agent only as prompt data.
- **Agent config removed:** a step deletes `CLAUDE.md`, `AGENTS.md`, `.mcp.json` and `.claude/` from the checkout before the agent runs.
- **Checkout action:** pinned to the full SHA for `actions/checkout` v7.0.1, which I resolved with `gh` as the latest release.
- **`persist-credentials`:** I left it `true` on purpose. The agent pushes with it, and the same token is already in its environment.
- **Injection-safe values:** the comment body reaches the agent only as an action input, never in a `run:` block. Values used in the shell step go through `env:`.
- **Prompt:** it now says the comment, branch name and repo content are data. That is a hint to the model, not a control.
- **Limits:**
  - A 15-minute `timeout-minutes`.
  - `concurrency` per PR, with no cancelling, so an agent mid-push isn't killed.
  - `GITHUB_TOKEN` is passed as `github.token`.

## What you still need to do
1. **Pin `acme/coding-agent`.** I couldn't resolve it (no release or tag visible to me), so it's still `@v1` with a TODO comment. Pin it to a commit SHA before enabling.
2. **Set an allowlist if the action offers one.** Restrict its tools to named commands, with no general shell. I don't know the action's inputs, so I didn't invent any.
3. **Add `.github/CODEOWNERS`.** Cover `.github/`, `Makefile` and anything else a workflow runs. The agent can't edit workflow files with `GITHUB_TOKEN`, but it can edit `Makefile`, which `ci.yml` runs.
4. **Protect the branches and add a dependabot config.** There's no `dependabot.yml` for the `github-actions` ecosystem. Enable branch protection or rulesets so the agent's pushes to PR branches are reviewed before merge.
5. **Put `MODEL_API_KEY` in an environment** with required reviewers if you want a second gate. I didn't add this because it changes how you operate.
6. **Check the Actions settings.** Fork-PR approval should be on.

I also noticed `ci.yml` pins checkout at v5.0.0, which is behind the current v7.0.1. I left it unchanged.
