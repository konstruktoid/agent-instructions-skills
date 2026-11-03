I rewrote `.github/workflows/assistant.yml` to close the main holes. The YAML parses, but I haven't run the workflow on GitHub, so it's untested end to end.

**What I changed**
1. **Only trusted people can trigger it.** The old workflow ran for any comment from anyone, and it also ran on plain issues. On a public repo that would let a stranger spend your `MODEL_API_KEY` and get a write-capable agent to act on text they wrote. The job now runs only on pull-request comments whose author is `OWNER`, `MEMBER` or `COLLABORATOR`. The check is in the job's `if:`, so secrets are never loaded for anyone else.
2. **Fork PRs are refused.** The old checkout of `refs/pull/N/head` would have put fork code in front of an agent holding secrets and a write token. A new first step looks up the PR's head repository and fails if it isn't this repo. It also outputs the branch name and commit SHA, and the checkout uses that SHA so the code can't change between the check and the run.
3. **Permissions are least-privilege.** `write-all` is replaced by `permissions: {}` at the top level. The job itself gets only `contents: write` (to push) and `pull-requests: write`.
4. **The `edited` trigger is gone.** With it, a comment could be changed after the fact and run again. It now fires only on `created`.
5. **The prompt is hardened.**
   - It tells the agent that repository content and PR text are untrusted data, not instructions.
   - It tells the agent never to print secrets.
   - It limits pushes to the PR's own branch.
   - This is defence in depth, not a hard guarantee. The real protection is the author check, the fork refusal and the narrow token.
6. **Runs are bounded.** I added `timeout-minutes: 15` and a per-PR `concurrency` group so two comments can't push at the same time.
7. **The token is the job-scoped `github.token`.** The step that reads PR metadata passes values through `env`, never into the script text.

**What you still need to do**
- **Pin the actions.** Both `actions/checkout@v5` and `acme/coding-agent@v1` need to be pinned to full commit SHAs. I couldn't look up the real SHAs here, so I left `TODO` comments rather than invent them.
- **Expect CI not to re-run on agent pushes.** Pushes made with `GITHUB_TOKEN` don't trigger other workflows. If you want CI to run on the agent's commits, you'll need a GitHub App token. I didn't add one because that changes how the workflow authenticates.
- **Branch protection still applies.** The agent can push to any same-repo PR branch, so keep protected branches and required reviews on `main`.
- **Decide whether `edited` should come back.** I dropped it for safety. If you rely on re-running by editing a comment, tell me and I'll weigh that with you.
- **Check the commit state.** The checkout is of a SHA, so the agent starts on a detached HEAD. If `acme/coding-agent` doesn't handle pushing from that state, switch the checkout `ref` to `steps.pr.outputs.head_ref`.
