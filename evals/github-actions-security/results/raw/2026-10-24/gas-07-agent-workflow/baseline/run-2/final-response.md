I've hardened `.github/workflows/assistant.yml`. I haven't run it or linted it, so test it on a throwaway PR before you enable it.

**What was wrong and what I changed**

1. **Anyone could trigger it.** Any commenter, on any issue or PR, could start a run that had your model key and write access. The job now runs only when all of these hold:
   - the comment is on a pull request;
   - the commenter's `author_association` is OWNER, MEMBER or COLLABORATOR;
   - the commenter isn't a bot.
2. **`permissions: write-all`.** The workflow now has `permissions: {}` at the top. The job gets only `contents: write` (to push) and `pull-requests: write`.
3. **Fork PRs.** The old workflow checked out `refs/pull/N/head`, so a fork's code would run next to your secrets. The agent would also read attacker-written files, which is a prompt-injection route. A new step looks up the PR's real head through the API and fails if the head repo isn't this repo. It then checks out that repo and branch. The old ref expression also broke on plain issues, which have no PR ref.
4. **`edited` trigger removed.** Otherwise a comment could be changed after it was posted and re-run the agent. Now only `created` triggers it.
5. **Smaller fixes.**
   - A `timeout-minutes: 20` cap stops a runaway agent.
   - A per-PR `concurrency` group stops two agents pushing to the same branch at once. It doesn't cancel a run that's already in progress.

**Behaviour you keep:** a maintainer comments on a same-repo PR, the agent makes the change and pushes it, and the prompt is unchanged.

**What I didn't do, and what to check**
- **Pinning:** `actions/checkout@v5` and `acme/coding-agent@v1` are still on mutable tags. I can't look up commit SHAs from here. Pin both to full SHAs, especially the third-party agent, which handles `MODEL_API_KEY`.
- **Fork PRs:** they're now refused. Supporting them safely would need a separate design with no secrets and no push rights.
- **Repo settings:** the workflow can't enforce these, so set them yourself.
  - Add branch protection or rulesets on your main branches so the agent can't push to them directly.
  - Under Settings → Actions, set the default workflow token to read-only.
- **Pushes and CI:** pushes made with `GITHUB_TOKEN` don't trigger other workflows, so `ci.yml` won't run on the agent's commits. This was already true before my changes. If you want CI to run, you'd need a GitHub App token or a similar approach.
- **Maintainer comments are still trusted:** a maintainer's comment text goes straight into the prompt. A maintainer who pastes untrusted text could be used to inject instructions. That's acceptable only because the commenter is a trusted maintainer and the agent is limited to this branch's write access.
