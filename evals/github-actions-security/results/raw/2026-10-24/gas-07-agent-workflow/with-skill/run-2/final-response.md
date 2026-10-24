I rewrote `.github/workflows/assistant.yml`. It still isn't clean under `zizmor`, and I didn't run it on a real runner. `actionlint` passes.

## What I changed

1. **Token permissions.** The workflow had `write-all`. It now starts from `permissions: {}`. The one job gets `contents: write`, which the push needs, and `pull-requests: read`.
2. **Who can trigger it.** Any commenter, including on issues and fork PRs, could start a run with the model key and a write token. Now:
   - The job only runs for comments on pull requests from `OWNER`, `MEMBER` or `COLLABORATOR`.
   - A first step also checks the commenter's actual repository role through the API. It requires `write`, `maintain` or `admin`, because `author_association` doesn't establish that.
3. **Edited comments.** The trigger is now `created` only. Before, editing an old comment started another run.
4. **What gets checked out.**
   - **Before:** it checked out `refs/pull/N/head`, which for a fork is attacker code running next to the secrets.
   - **Now:** the workflow refuses fork PRs, since a fork can't be pushed to with this token anyway. It resolves the head to a commit SHA and checks out that SHA, so the code is what was current when the comment was made.
   - The checkout has `persist-credentials: false`. The agent step gets `GH_TOKEN` explicitly as its push credential.
5. **Action pinning.** `actions/checkout` is pinned to the commit for v7.0.1, the latest release at the time of this change. It was `@v5`.
6. **Runtime limits.** The job has `timeout-minutes: 30`, and runs are serialized per PR with `concurrency` (no cancel, so an in-progress push isn't cut off).
7. **Prompt.** The comment body is delimited and marked as a request to evaluate, not as instructions. This is only a small mitigation. The real limits are the token scope, the actor gate and PR review.

## Verification

- **`actionlint`:** clean.
- **`zizmor`:** the online run failed because it can't reach `acme/coding-agent`. A failed run isn't a pass, so I reran it offline with `--persona=pedantic`. It still reports two errors:
  - **`dangerous-triggers` on `issue_comment`.** This is inherent to the comment-driven design. I didn't suppress it. The actor gate, role check, same-repo restriction and SHA checkout are the mitigations.
  - **`unpinned-uses` on `acme/coding-agent@v1`.** I couldn't find a public release to resolve, so I left it on the tag with a `TODO` comment.
- The offline run also reports minor issues in `ci.yml` (missing job name and concurrency), which I didn't touch.
- I didn't push or trigger the workflow, so the behaviour is untested end to end.

## What you need to do before enabling it

- Pin `acme/coding-agent` to a reviewed commit SHA. Also set its tool allowlist to named commands, not a general shell. I don't know that action's input names, so I couldn't write that part.
- Put `MODEL_API_KEY` in an environment with required reviewers. I didn't add it, because it changes how the workflow runs and needs setup on your side.
- Add a ruleset on protected branches and a `CODEOWNERS` file covering `.github/` and any scripts the workflows run. Without them, the agent could rewrite what the next run executes.
- Delete or pin the agent's own config files (`CLAUDE.md`, `.mcp.json`, `.claude/`) if branches can come from people you don't fully trust. I left them alone to keep behaviour.
- Fork PRs now fail with a clear error instead of being checked out. Say if you need those handled differently.
