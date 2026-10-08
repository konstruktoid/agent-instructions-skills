I rewrote `.github/workflows/assistant.yml`. I haven't run it or linted it, so test it on a throwaway PR before you enable it.

**What I changed and why**

1. **Only maintainers can trigger it.**
   - Before, any commenter on any issue or PR could start the job. On a public repo that means anyone could run the agent with your secrets and a write token.
   - The job now needs the comment to be on a PR, from an author with `OWNER`, `MEMBER` or `COLLABORATOR` association.
2. **Token permissions are minimal.** `permissions: write-all` is gone. The workflow default is `{}`, and the job gets only `contents: write` and `pull-requests: write`.
3. **Fork PRs are refused.**
   - The old workflow checked out `refs/pull/N/head`. For a fork PR, that hands attacker-controlled files to an agent holding `MODEL_API_KEY` and a write token. The files could carry prompt injection or malicious build scripts.
   - A new first step looks the PR up through the API. It fails unless the PR is open and its head is a branch in this repository.
   - Checkout now uses that branch name. This also fixes the old `ref:` expression, which would have fallen back to a bad ref on non-PR events.
4. **The trigger is `created` only.** I dropped `edited`, because a comment could be changed after a maintainer had read it, and each edit would re-run the agent.
5. **The agent gets more guardrails.**
   - Added `concurrency` per PR, so two comments can't make the agent push over itself.
   - Added `timeout-minutes: 30`.
   - The prompt now says the comment is the task. It tells the agent to ignore instructions in repo files or PR text that ask for secrets, workflow changes or external contact. It also names the target branch.
   - `GH_TOKEN` now uses `github.token`, which is the same token as before.

**What you should still do**
- **Pin the actions.** Pin `actions/checkout@v5` and `acme/coding-agent@v1` to full commit SHAs. I couldn't resolve them offline. `acme/coding-agent` is third-party code that receives your API key, so this matters most there.
- **Protect your branches.**
  - The agent can push to any same-repo PR branch, so protect `main` with required reviews.
  - Don't let the agent bypass branch protection.
  - Add a CODEOWNERS entry for `.github/workflows/`. A push from `GITHUB_TOKEN` can't modify workflow files without the `workflows` permission, which I deliberately didn't grant.
- **Check what the agent can do.** Prompt text can't stop it from doing something harmful, so look at its tool and network settings.
- **Use an environment.** Consider a GitHub Environment with required reviewers for `MODEL_API_KEY`, if you want an approval step before each run.

**Behaviour you might notice**
- PRs from forks no longer work. Same-repo branches behave as before.
- Pushes made with `GITHUB_TOKEN` don't trigger CI on their own, as before.
