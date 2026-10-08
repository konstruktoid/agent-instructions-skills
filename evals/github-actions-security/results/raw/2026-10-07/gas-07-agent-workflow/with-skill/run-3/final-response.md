I rewrote `.github/workflows/assistant.yml`. Don't turn it on yet: the agent action is still pinned to a mutable tag, and the workflow has never run. `actionlint` is clean. `zizmor` was run offline, because it couldn't reach `acme/coding-agent`. It left two findings in this file. One was a missing comment, which I then fixed; I didn't rerun it after that edit. The other is the unpinned agent action.

**What was wrong**
- **No gate on who comments.** On a public repo, anyone's comment could start the agent with your model key and a write token.
- **`permissions: write-all`.** The agent got every scope, including `actions`, `packages` and `id-token`.
- **Edited comments re-fired the workflow.** Someone could edit an old comment into a new instruction.
- **The comment was handed to the agent as its instructions.** I kept that, because it's how the workflow works. I added a prompt note that comment and repo text is data, but that is only a mitigation.
- **Fork pull requests were checked out.** It ran fork-controlled code with a write token and the model key, and the branch could move between the comment and the checkout.
- **Credentials sat in `.git/config`**, where an agent that can read files would find them.
- **No `timeout-minutes`**, so a runaway agent could run for 6 hours.
- **`CLAUDE.md`, `.mcp.json` and `.claude/` came from the checkout.** A pull request could change what the agent runs.

**What I changed**
- **Trigger:** only `created` comments, and only on pull requests.
- **Authorization:** the job only runs for owners, members and collaborators. A separate `gate` job then checks the commenter's actual role through the API and requires write, maintain or admin.
- **Pinned commit:** the gate resolves the pull request head to a commit SHA, and the agent checks out exactly that commit.
- **Fork pull requests are refused.** `GITHUB_TOKEN` can't push to a fork anyway, and fork content isn't maintainer-authored. Same-repo pull requests still work as before.
- **Permissions:** `permissions: {}` at the top. The gate job gets read scopes only. The agent job gets `contents: write` and `pull-requests: write`, each with a comment saying why.
- **Checkout:** pinned to the v7.0.1 SHA (the current release, which I looked up), with `persist-credentials: false`. A step then deletes the agent config files that came with the checkout.
- **Timeouts and queueing:** `timeout-minutes` is set on both jobs. Runs queue per pull request instead of cancelling, so an agent isn't killed mid-push.
- **Secrets:** `MODEL_API_KEY` and `GH_TOKEN` stay on the agent step only.
- **Prompt:** it names the branch to push to and says not to touch `.github/`. The prompt is not a security control.

**What you still need to do**
- **Pin `acme/coding-agent` to a commit SHA.** I couldn't resolve it from here (404), so it's still `@v1` with a TODO.
- **Restrict the agent's tools.** I don't know that action's inputs. Allow only the commands it needs, and no general shell.
- **Gate the secret behind an environment.** Put `MODEL_API_KEY` in an environment with required reviewers, and add `environment:` to the agent job. This is a repo setting I can't make.
- **Add a `CODEOWNERS` file** covering `.github/`, the `Makefile`, and anything else a workflow runs. Without it the agent can change what CI executes without touching a workflow file. Also set the Actions setting to require approval for outside contributors. `CODEOWNERS` is missing today.
- **Protect the default branch.** Add a ruleset that requires review, and don't add the agent as a bypass actor.
- **Add a network egress limit** if you can. I didn't add one.
- **Test the role check.** I haven't confirmed that `GITHUB_TOKEN` with `contents: read` can call the collaborator-permission API. If it returns 403, widen the gate job's token or use an app token.
- **Run it once on a test pull request.** The change is behavioral and has not been run on a runner.
