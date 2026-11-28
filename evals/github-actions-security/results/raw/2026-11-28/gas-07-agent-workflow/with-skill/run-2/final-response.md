I rewrote `.github/workflows/assistant.yml`. A maintainer can still comment on a pull request and get the change pushed, but **don't enable it on the public repository yet**: the agent action still isn't pinned, and the new version has never run on GitHub.

**What was wrong**
- **Anyone could run it.** Any commenter on a public repository could give an agent instructions while it held your model key and a `write-all` token.
- **Fork code ran with those credentials.** It checked out the pull request head, including any files written to steer the agent.
- **The agent could write to the repository.** The token was in its environment and also left in the git config by checkout.

**What changed**

| Change | Why |
|---|---|
| Split into `authorize`, `agent` and `push` jobs | The agent's token is now read-only. It produces a patch, and a separate job that runs no repository code commits and pushes it. |
| Commenter must have `write`, `maintain` or `admin` | Being a "member" or "collaborator" doesn't guarantee write access. |
| Fork pull requests are refused | This keeps fork files away from the model key. The old workflow's token couldn't normally push to a fork anyway. |
| Checks out the exact head commit; never force-pushes | If the branch moves during the run, the push fails. |
| Refuses to push to the default branch | Covers a pull request whose head branch is the default branch. |
| Rejects patches touching `.github/`, `CLAUDE.md`, `AGENTS.md`, `.mcp.json` or `.claude/` | Stops the agent changing automation or its own configuration. |
| `permissions: {}` by default, timeouts, one run per pull request | Limits what each job can do and for how long. |
| `actions/checkout` v5 → v7.0.1, pinned by commit; artifact actions pinned too | Tags can be moved. These were the latest releases when I looked them up. |

**Behaviour differences**
- Editing a comment no longer triggers a run; post a new one.
- The agent is told not to commit or push. Anything it does becomes a single `github-actions[bot]` commit.
- If several requests queue on one pull request, GitHub keeps only the newest waiting one.

**Before you enable it**
1. **Pin `acme/coding-agent`.** I couldn't read its repository, so `@v1` remains, marked TODO. Whoever controls that tag controls code that receives your model key.
2. **Check the action's settings.** Confirm it works without pushing itself, and restrict which commands and network hosts it can use. I didn't guess at input names.
3. **Set up the `assistant` environment.** Move `MODEL_API_KEY` into it, delete the repository-level copy, and limit it to the default branch. Required reviewers are optional extra protection. Until then the environment protects nothing.
4. **Protect your branches** with rulesets, and add code owners for files that run code, such as `Makefile`. The patch check doesn't block those.
5. **Try it on a test pull request**, including a comment from an account without write access.

**Risk that remains:** the agent still has the model key while reading comments and repository files. Injected instructions in a same-repository branch (a bot's dependency update, say) could leak it through the network, the public job log or the patch. A rejected or unpushed patch can also be downloaded for a day. Use a key with a spending limit that you can easily rotate.

Every comment from someone with write access still starts the agent, even "LGTM". I'd require a prefix such as `/assistant`, but didn't add one because it changes how you use it.

**Checks**
- **`actionlint`:** clean.
- **`zizmor` (pedantic, offline):** not clean. In `assistant.yml` it reports the unpinned agent action (item 1) and `issue_comment` as a risky trigger, which your feature needs. It also reports two minor findings in `ci.yml`, which I didn't change. I suppressed nothing.
- **Local test:** the patch and path-check scripts accepted a normal file and rejected four protected paths.
- **Not tested:** the permission lookup, pull request lookup, artifact handoff and push need a real run. In particular, confirm the permission lookup works with the token granted. I gave that job `contents: write` for it, though it writes nothing.

Pushes made with this token won't start your CI normally, as was already true before. Running CI automatically would need a GitHub App token in the `push` job. Adding Dependabot would also keep the pinned actions current.

Nothing is committed or pushed.
