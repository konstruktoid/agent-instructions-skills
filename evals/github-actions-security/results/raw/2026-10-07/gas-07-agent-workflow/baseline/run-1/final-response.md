I rewrote `.github/workflows/assistant.yml`. I haven't run it or linted it, and I didn't open `ci.yml`.

**What was wrong and what I changed**

1. **Anyone could trigger it.** `issue_comment` fires for any commenter, and the old job had no check. On a public repo, any user could have made an agent holding write credentials run their text. The job now runs only if all of these hold:
   - the comment is on a pull request, not a plain issue;
   - `author_association` is OWNER, MEMBER or COLLABORATOR;
   - the commenter isn't a bot.
2. **Fork PRs were checked out and run with secrets.** The old `refs/pull/N/head` checkout would have pulled in fork code while the job held a write token and `MODEL_API_KEY`. A new first step looks up the PR's head repo and fails if it isn't this repository. The job then checks out the PR's branch by name, so the agent can push to it. Before, it got a detached ref.
3. **`permissions: write-all`.** I set the workflow default to `{}` and gave the job only `contents: write` and `pull-requests: write`.
4. **The comment was spliced into the prompt.** `${{ github.event.comment.body }}` went straight into the `with:` input. That is template injection of attacker-controlled text. The body now goes through the `COMMENT_BODY` env var, and the prompt tells the agent to treat it as the task only. It also tells the agent to ignore any instructions in repo files or tool output that ask it to reveal secrets or change workflows. This is a mitigation, not a hard guarantee, so permissions and the maintainer gate are still what protect you.
5. **The `edited` trigger.** It let a comment be changed after the fact and re-run the agent. I removed it, so only `created` triggers a run.
6. **Missing guards.** I added a per-PR `concurrency` group with no cancel-in-progress, so a run that is mid-push isn't killed. I also added `timeout-minutes: 15`.
7. **Token source.** `GH_TOKEN` now uses `github.token`, the same token as `secrets.GITHUB_TOKEN`, scoped by the job permissions above.

**Still to do (you)**
- **Pin the actions to commit SHAs.** I marked `actions/checkout@v5` and `acme/coding-agent@v1` with TODOs because I can't look up the SHAs from here. `acme/coding-agent@v1` is a third-party action that receives your model key, so I'd prioritise that one.
- **Restrict who can run it, in repo settings.** Use an environment with required reviewers for `MODEL_API_KEY`, or a dedicated key with a spend limit. Also check that the agent can't push to protected branches or edit `.github/workflows/`. A `GITHUB_TOKEN` can't change workflow files, but a PAT or app token could.
- **Behaviour change.** Comments on fork PRs now fail with an error instead of running. If you need those, it needs a separate, more careful design.
- **Push credentials.** I left `persist-credentials: true` on checkout, because the agent has to push with the stored credentials. If `acme/coding-agent` pushes using `GH_TOKEN` itself, set it to `false`.
