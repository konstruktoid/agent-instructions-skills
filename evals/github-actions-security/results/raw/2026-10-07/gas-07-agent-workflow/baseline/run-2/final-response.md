I've rewritten `.github/workflows/assistant.yml` and kept the behaviour: a maintainer comments on a PR, and the agent makes the change and pushes it. I haven't run it, and I didn't check `ci.yml`.

**What I changed**

1. **Only maintainers can trigger it.** The old workflow ran for any commenter on any issue or PR, and on a public repo anyone can comment. It now requires a pull request and a comment author whose association is `OWNER`, `MEMBER` or `COLLABORATOR`.
2. **Permissions are minimal.** `write-all` is replaced with a workflow default of `{}`. The job gets only `contents: write` (to push) and `pull-requests: write`.
3. **Fork PRs are refused.**
   - The old checkout fetched `refs/pull/N/head` and ran that code with `MODEL_API_KEY` and a write token. A fork PR could use that to steal the secrets or push to the repo.
   - A new first step looks up the PR's head repo and fails if it isn't this repo. The checkout then uses the head branch name.
   - A side benefit is that the agent can now actually push, which `GITHUB_TOKEN` can't do to a fork.
4. **No re-runs on edits.** I dropped the `edited` trigger. An edit would otherwise start a second agent run, and it let a comment's content change after a maintainer had looked at it.
5. **Safer prompt.** The comment is wrapped in a delimiter. The prompt tells the agent to treat PR and file content as data, not instructions, to keep secrets out of output, and to push only to the PR branch. This reduces prompt-injection risk but doesn't remove it.
6. **Operational limits.** I added a 15-minute timeout and a per-PR `concurrency` group so two runs can't push to the same branch at once.
7. **Cleanup.** The odd `issue.number && format(...)` expression is gone. `GH_TOKEN` now uses `github.token`.

**Still to do or be aware of**

- **Pin the actions to commit SHAs.** I marked `actions/checkout` and `acme/coding-agent` with TODOs because I can't look up the SHAs here. `acme/coding-agent@v1` is third-party and runs with your secrets, so pinning matters most for it.
- **Fork PRs now fail.** If you want the agent to work on them, that needs a separate, deliberately designed flow.
- **CI won't run on the agent's pushes.** Pushes made with `GITHUB_TOKEN` don't trigger other workflows. If you want CI on them, use a GitHub App token or a deploy key.
- **Protect your branches.** The agent can push to any same-repo PR branch, including a PR branch someone made from `main`. Branch protection and required reviews on `main` are your backstop.
- **Check the environment.** If `MODEL_API_KEY` is a repo-level secret, consider moving it to an environment that requires approval.
