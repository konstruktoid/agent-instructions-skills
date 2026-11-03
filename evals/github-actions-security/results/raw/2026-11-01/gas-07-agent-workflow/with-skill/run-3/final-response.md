I hardened `.github/workflows/assistant.yml`, but it isn't ready to turn on yet. The agent action is still on a mutable tag. `actionlint` is clean. `zizmor` (v1.31.1, pedantic, offline) still reports two high findings, which I left on purpose and explain below. I didn't run the workflow on a runner, so the behaviour is untested until a real PR comment exercises it.

**What I changed**
- **Permissions:** `write-all` is now `permissions: {}` at workflow level. The job gets only `contents: write` (the agent has to push) and `pull-requests: read`.
- **Who can start it:** the old workflow ran for any commenter, on issues as well as PRs, with the model key and a write-all token.
  - The job now only runs for comments on pull requests, from `OWNER`, `MEMBER` or `COLLABORATOR`, and not from bots.
  - `author_association` isn't a real permission check (a read-only collaborator passes it), so the first step looks up the commenter's actual role and requires write, maintain or admin.
- **Trigger:** `types: [created]` only. Before, editing an old comment re-ran the agent.
- **Fork PRs:** the job fails if the PR comes from a fork. Fork code would otherwise be checked out and run next to the model key and a write token. `GITHUB_TOKEN` can't push to a fork anyway, so this doesn't cost you any working behaviour.
- **Checkout:** it now checks out the PR head commit SHA, resolved when the comment arrives, instead of `refs/pull/N/head`. The branch could move between the comment and the checkout. I also set `persist-credentials: false` and pinned `actions/checkout` to v7.0.1 (`3d3c42e…`), the current release I looked up. It was `@v5`.
- **Prompt:** the comment still goes in as an action input, never into a `run:` block. The prompt now says to treat the comment and repo content as data and to push to the current PR branch. This is only a hint to the model. The real limits are the token scope and the gates above.
- **Smaller fixes:**
  - The model key is only on the agent step.
  - `GH_TOKEN` is now `github.token`.
  - The job has `timeout-minutes: 20`.
  - `concurrency` is keyed per PR without cancelling, because cancelling an agent mid-push could leave a half-pushed branch.

**What's left, and what you need to do**
1. **`acme/coding-agent@v1` is unpinned.** `gh` returned 404 for that repo, so I couldn't resolve a real release or commit SHA, and I won't make one up. Pin it to a full SHA before enabling. There's a TODO in the file.
2. **`zizmor` flags `issue_comment` as a dangerous trigger.** That's inherent to a comment-driven workflow. The gates above are the mitigation, so I didn't suppress it.
3. **Repo settings I couldn't change from here:**
   - Put `MODEL_API_KEY` in an environment with required reviewers, and add `environment:` to the job.
   - Protect the default branch with a ruleset so the agent can't push there.
   - Add `CODEOWNERS` covering `.github/` and anything else a workflow executes. This repo has no `CODEOWNERS` and no `dependabot.yml`.
   - Check what the action's tool allowlist permits. I couldn't see its options, so I didn't touch them.
   - Keep the agent's identity off any ruleset bypass list.

**Not done**
- The checked-out branch can still contain `CLAUDE.md` or `.mcp.json` files that the agent reads. I judged this acceptable because only same-repo branches by writers reach the agent now.
- `ci.yml` is still on `actions/checkout` v5.0.0. I left it alone since it's outside this request.
