I hardened `.github/workflows/assistant.yml`. I haven't run it or committed anything, so none of it is tested, and the `persist-credentials: false` change could break the push (see below).

**What I changed**

1. **Only maintainers can trigger it.** The old workflow ran for any commenter, and on a public repo anyone can comment. The job now runs only when the comment is on a pull request and the author is an `OWNER`, `MEMBER` or `COLLABORATOR`.
2. **Fork PRs are refused.** The old workflow checked out `refs/pull/N/head` with the secrets and a write token available. On a fork PR that would run attacker-controlled code with both. A new first step looks up the PR's head repo and fails unless it is this repository. It then checks out the head branch by name, which also gives the agent a branch it can push to.
3. **Permissions are reduced.** `write-all` is now `permissions: {}` at the top level. The job gets only `contents: write` (to push) and `pull-requests: write`.
4. **The `edited` trigger is gone.** Re-running on an edited comment would act on text that wasn't re-checked.
5. **Prompt-injection guard.** The prompt now marks the comment as the task description and tells the agent to treat the comment and repository content as data. It also tells the agent not to expose secrets and to push only to the current PR branch. This is a mitigation, not a hard boundary. The real protections are items 1–3.
6. **Smaller changes.** I set `persist-credentials: false` on checkout so the token isn't left in `.git/config`. I added a per-PR `concurrency` group so two comments can't push over each other. I added `timeout-minutes: 15` to cap a runaway agent.

**Things to check**

- **Push access:** with `persist-credentials: false`, the push depends on `acme/coding-agent` using the `GH_TOKEN` it is given. I don't know how that action pushes. If it relies on git credentials from checkout, remove that line.
- **Action pinning:** `acme/coding-agent@v1` and `actions/checkout@v5` are still tag-pinned. I couldn't look up commit SHAs offline, so pin both to full SHAs, especially the third-party agent action, which receives your secrets.
- **Repo settings:** check that "Require approval for outside collaborators" is on. Branch protection on your default branch also limits the damage if the agent misbehaves. The workflow can only push to PR branches, but protection is still a useful backstop.
- **Fork contributions:** the assistant no longer works on PRs from forks, which is deliberate. If you need that, the safer design is to have it open a separate PR rather than push to the fork.

I didn't read `ci.yml`, so it may have similar problems.
