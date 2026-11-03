I hardened `.github/workflows/assistant.yml`. I haven't run it, and the YAML isn't validated.

**What I changed and why**
1. **Commenter gate (the main hole).** The workflow ran for any comment on any issue or PR, so anyone on a public repo could trigger an agent with write access and your API key. It now runs only on PR comments from `OWNER`, `MEMBER` or `COLLABORATOR`. GitHub sets `author_association`, so a commenter can't fake it.
2. **Permissions.** I replaced `write-all` with `permissions: {}` at the top. The job itself gets only `contents: write` and `pull-requests: write`, which is enough to push and comment.
3. **Fork PRs.** The old workflow checked out the PR head and ran the agent on it with secrets, so a fork PR could run attacker-controlled code. A new first step looks up the PR's head repo and fails unless it's this repo. `GITHUB_TOKEN` can't push to forks anyway, so you lose nothing.
4. **`edited` trigger removed.** A comment could be approved and then rewritten, and each edit re-ran the agent with secrets. It now fires on `created` only.
5. **Concurrency and timeout.** There is one run per PR at a time, and I set `cancel-in-progress: false` so a run isn't killed mid-push. The job has a 15-minute timeout to cap runaway agent spend.
6. **Checkout ref.** The old conditional could silently check out the default branch. I simplified it, since the `if:` now guarantees a PR.

**Left for you**
- **Pin the actions.** `actions/checkout@v5` and `acme/coding-agent@v1` are still on mutable tags. I marked them `TODO` because I can't look up commit SHAs from here. Pin both, especially the third-party agent, since it holds your key and a write token.
- **Prompt injection.** The comment body is still interpolated into the prompt. Since only maintainers can trigger it, that's acceptable. But the agent also reads PR contents, which a contributor wrote, so keep its permissions narrow. Consider branch protection or required review so its pushes can't merge unreviewed.
- **Token and credentials.** I kept the credentials that `checkout` persists, because the agent has to push. If `acme/coding-agent` can push using only `GH_TOKEN`, add `persist-credentials: false`.
- **Fork PRs.** If you want the agent to work on fork PRs, that needs a different design. Don't loosen the same-repo check.
- **`ci.yml`.** I didn't review it.
