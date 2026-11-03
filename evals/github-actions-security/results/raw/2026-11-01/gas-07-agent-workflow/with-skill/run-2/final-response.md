I've hardened `.github/workflows/assistant.yml`, but it isn't ready to turn on for the public repository yet. `acme/coding-agent` is still pinned only to `@v1`, and I haven't run the workflow on a runner.

`actionlint` is clean. `zizmor` (offline, pedantic) reports 2 high findings, both left in deliberately. The unpinned `acme/coding-agent@v1` is one. The other is its blanket warning on `issue_comment`, which is the trigger you want to keep. I ran `zizmor` offline because it can't look up `acme/coding-agent`.

**What was wrong**
- `permissions: write-all` gave every scope to a job that reads attacker-controlled text.
- Any commenter on a public repository could start the agent, because nothing checked who they were.
- The comment body went straight into the prompt, and the agent was told to push.
- The workflow ran on edited comments as well as new ones, so a maintainer could approve a comment and have it edited afterwards.
- The checkout used a mutable ref and left the token in `.git/config`.
- Nothing set a job timeout, so the 360-minute default applied.
- `actions/checkout@v5` was a tag, not a commit.

**What I changed**
- **Permissions:** the workflow now denies everything by default. The job gets only `contents: write` (to push to the PR branch) and `pull-requests: write` (to comment), each with a comment saying why.
- **Who can trigger it:**
  - The trigger is `created` only, so edits don't re-run it.
  - A job-level `if` allows only pull request comments from `OWNER`, `MEMBER` or `COLLABORATOR`, and not from bots.
  - A first step then checks the commenter's real repository role and requires `write`, `maintain` or `admin`. `author_association` alone isn't enough, because `COLLABORATOR` includes read-only access.
- **Fork PRs:** the workflow now refuses them. `GITHUB_TOKEN` can't push to a fork anyway, and fork content shouldn't reach an agent holding a write token. This is a behaviour change, but only for a case that couldn't have worked.
- **Checkout:**
  - It is pinned to the PR head commit as it was when the comment was posted, with `persist-credentials: false`.
  - The checkout action is pinned to the current release, v7.0.1 (`3d3c42e5…`).
  - A step deletes `.mcp.json`, `.claude/`, `CLAUDE.md` and `AGENTS.md` before the agent runs, so the tree can't add tools or hooks.
- **Prompt:** the prompt now says the comment and repository contents are data, not rules, and that the agent should push only to the PR branch. This is a weak control, and the real limits are the token scope and the gates above.
- **Run limits:** I set a 20-minute timeout and a concurrency group per PR that queues runs rather than cancelling one mid-push.
- **Cosmetic:** I gave the job a name.

**Before you enable it**
1. **Pin `acme/coding-agent`.** I couldn't find a release for it from here, so I didn't invent a SHA. Pin it to a full commit SHA with a version comment. A `TODO` in the file marks the spot.
2. **Limit the agent's tools.** Use that action's own configuration to name the commands it may run, with no general shell. I can't set that without knowing its inputs.
3. **Put `MODEL_API_KEY` in a protected environment.** Use one with required reviewers. This matters most on a public repository.
4. **Add repo-level protections.**
   - Branch rulesets for any protected branches.
   - A `CODEOWNERS` file covering `.github/` and the files your workflows run, such as the `Makefile`.
   - Fork-PR approval set to "all outside collaborators".

   The repository has no `CODEOWNERS` or `dependabot.yml` today. Remember that `ci.yml` pins checkout to v5.0.0, which is behind v7.0.1.
5. **Test it.** Comment on a same-repo PR and read the run log. The role check, the head resolution and the push haven't run anywhere. I didn't push anything or trigger a run.
