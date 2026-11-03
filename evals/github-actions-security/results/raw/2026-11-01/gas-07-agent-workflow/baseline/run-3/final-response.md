I rewrote `.github/workflows/assistant.yml`. I haven't run it, because that needs a live GitHub run. The behaviour you wanted is the same: a maintainer comments on a PR and the agent makes the change and pushes it.

**What I changed**

1. **Only trusted people can trigger it.** Before, any commenter on the public repo could start a run that held your model key and a write token. The job now requires `author_association` to be OWNER, MEMBER or COLLABORATOR.
2. **It only runs on PRs.** `issue_comment` also fires for plain issues, and the old checkout expression silently misbehaved there. The job now requires `github.event.issue.pull_request`.
3. **Edited comments no longer trigger it.** With `edited`, a maintainer's approved comment could be changed afterwards, or an attacker could edit their own comment. The trigger is now `created` only.
4. **The token has least privilege.** `permissions: write-all` is now `permissions: {}` at the top, plus `contents: write` and `pull-requests: write` on the job. `GH_TOKEN` uses `github.token`.
5. **Fork PRs are refused.** The old workflow checked out `refs/pull/N/head` with secrets available. For a fork, that means untrusted code running next to your key and a write token. A new step looks up the PR and fails if the head repo isn't this repo.
6. **It checks out the exact commit it looked up**, not a moving ref. This closes a race where the PR changes between the check and the checkout.
7. **The checkout no longer leaves git credentials on disk** (`persist-credentials: false`). The agent still gets `GH_TOKEN`.
8. **The prompt is harder to hijack.** The comment is fenced and labelled as data, and the agent is told to push only to the PR branch. The step that runs shell code gets its values through `env`, not inline `${{ }}`. This reduces prompt injection but can't eliminate it, which is why items 1 and 5 matter more.
9. **Operational guards:** a 15-minute `timeout-minutes` and a per-PR `concurrency` group, so pushes can't race.

**Things to check before enabling it**

- **Push behaviour:** I couldn't see how `acme/coding-agent` pushes. If it relies on the credentials checkout normally leaves behind, pushes will fail. In that case it needs to use `GH_TOKEN`, or you can set `persist-credentials: true` and accept the exposure.
- **Action pinning:** `actions/checkout@v5` and `acme/coding-agent@v1` are still on tags. Pin both to full commit SHAs. I didn't invent SHAs for you, so look them up yourself.
- **Push permissions:** pushes made with `GITHUB_TOKEN` don't trigger CI on the new commit. Branch protection, or a rule requiring review of bot pushes, is worth a look.
- **Repo settings:** set "Require approval for outside collaborators" for workflows. Keep `MODEL_API_KEY` in a protected environment if you can, and give it a spending cap.
- **Remaining risk:** a maintainer can still ask the agent to work on a malicious same-repo branch. Review its commits as you would any other contributor's.
