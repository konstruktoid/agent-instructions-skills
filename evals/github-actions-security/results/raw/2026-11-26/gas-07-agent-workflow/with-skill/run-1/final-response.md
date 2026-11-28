I've rewritten `.github/workflows/assistant.yml`, but **don't enable it on the public repository yet**: `acme/coding-agent@v1` is still unpinned. It hasn't run on GitHub either.

**What was wrong**
- **Anyone could drive it.** Any comment from any user started an agent holding `write-all`, the model key and a push-capable token.
- **Fork code ran beside those secrets.** It checked out the pull request head, forks included, and the checkout left the token on disk.
- **Edits re-triggered it.** This included edits made by someone other than the original author.

**What it does now**

A maintainer still comments, the agent makes the change, and it gets pushed. It now takes three jobs:

| Job | Does | Can write to the repository? |
|---|---|---|
| `authorize` | Checks that the commenter has write access and records the head commit | Holds `contents: write` for the permission lookup; runs only its own script |
| `agent` | Edits files and saves them as a patch; has the model key | No |
| `push` | Applies the patch, commits and pushes; runs no agent or repository code | Yes |

I also:
- set `permissions: {}` at the top, with grants per job;
- limited the trigger to new comments on pull requests, ignoring bots;
- pinned the checkout and artifact actions to commit SHAs;
- stopped checkout saving credentials, and added timeouts and per-pull-request queuing;
- made the push fail if the branch moved after authorization.

**Behavior changes to check**
- Fork pull requests are refused, as are pull requests whose head is the default branch.
- Changes under `.github/` are refused.
- The agent no longer gets `GH_TOKEN`, so it can't reply on the pull request or call the GitHub API with it.
- The workflow does the commit and push, so the agent's own commit messages are lost.
- With several requests queued on one pull request, a newer one can replace an older pending one.

**Before you enable it**
1. **Pin the agent action.** I couldn't resolve `acme/coding-agent` without signing in, so I didn't invent a SHA. Pin it to a commit you've reviewed.
2. **Restrict the agent's tools.** I couldn't read the action's inputs. Allow only what it needs, with no general shell if possible. Also check that it works with a read-only token and leaves its changes in the working tree.
3. **Move the key.** Put `MODEL_API_KEY` in an `assistant` environment limited to the default branch, and delete the repository-level secret. Set a spending limit on the key.
4. **Protect branches.** Require review on the default branch, and add code owners for `Makefile` and other files that workflows execute.
5. **Test it.** Try a same-repository pull request, a fork, and a commenter without write access.

**Remaining risks**
- **Key leakage:** repository text can still try to steer the agent. It can't push directly, but it could leak the model key over the network or in logs, or put it into the patch. I added no network restrictions.
- **Patch contents:** the patch can change any file outside `.github/`, so review it like any outside contribution. It also picks up any untracked, non-ignored files the agent leaves behind.
- **CI won't run on the assistant's commit:** pushes made with `GITHUB_TOKEN` don't trigger workflows, which was also true before. A GitHub App token would fix that if you need required checks.

**Check results**
- `actionlint` passes.
- I tested the patch apply step and the `.github/` guard in a scratch repository.
- `zizmor` (pedantic, offline) still fails, with nothing suppressed:

| Finding | Where | Status |
|---|---|---|
| `unpinned-uses` (high) | `assistant.yml` | Real; blocks enabling (step 1) |
| `dangerous-triggers` (high) | `assistant.yml` | Comes with the comment trigger you want to keep; mitigated by the gates above |
| Two minor findings | `ci.yml` | Already there; I didn't touch that file |

`ci.yml` also pins checkout v5.0.0, while the latest is v7.0.1; that's worth a separate update.

If you'd rather not have every maintainer comment (even "looks good") start a run, I'd suggest requiring a `/assistant` prefix. I didn't add it because it changes how people use it.
