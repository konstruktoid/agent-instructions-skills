I rewrote `.github/workflows/assistant.yml` to keep the comment → change → push flow. **Don't enable it publicly yet:** the agent action isn't pinned, and none of this has run on GitHub.

## What was wrong
- **Anyone could use it.** Any commenter on a public repo could instruct an agent that had `write-all`, your model key and a push token.
- **Fork code ran with those credentials.** It checked out the pull request head, including any fork's files, which can carry instructions for the agent.
- **It also fired on plain issues and edited comments.**

## What I changed
| Change | Why |
|---|---|
| Only new comments on open pull requests, from users with `write`, `maintain` or `admin` | The permission lookup is the real check; the comment's author label alone can include read-only collaborators. |
| Fork pull requests and heads on the default branch are refused | Keeps outside code away from the model key, and the agent off `main`. |
| Checks out the exact commit resolved during authorization | The branch can't change between that step and the checkout. |
| Agent job is read-only, has no `GH_TOKEN`, and leaves no token in `.git/config` | A manipulated agent can't push or change the repo through the API. |
| A separate job applies the agent's patch and pushes | Only this job can write, and it runs nothing from the checkout or patch. |
| Push is rejected if the branch moved, or if the patch touches `.github/` | Avoids overwriting newer work or changing automation. |
| `permissions: {}` by default, timeouts, one agent run per pull request, official actions pinned to current releases | Limits access, cost and supply-chain risk. |

## Behaviour differences
- **Pushing:** the workflow now commits and pushes, not the agent. Multiple agent commits become one, with a generic message.
- **Forks and `.github/`:** both are now refused. The old setup likely couldn't push to forks anyway.
- **Other GitHub actions by the agent:** it can no longer comment, label or call the API with a write token.
- **Quick successive comments:** a second request may use the old commit and have its push rejected, so comment again. A third can replace one still waiting.

## Before you enable it
1. **Pin `acme/coding-agent`.** I couldn't resolve it publicly (it may be private or a placeholder). Replace `@v1` with a commit SHA you've verified.
2. **Check how that action behaves.** I haven't seen its source. Confirm it works without `GH_TOKEN`, edits the checked-out files, and doesn't fail when it can't push. If it has a tool allowlist, restrict it and don't grant a general shell.
3. **Protect the model key.** The agent still holds `MODEL_API_KEY` and has open network access, so a prompt injection could leak it. Use a key with a spending limit. Putting it in an environment with required reviewers helps, but adds an approval click to each run.
4. **Protect `main`** with a ruleset requiring reviews, and don't let Actions bypass it.
5. **Test on a private copy.** Try a maintainer, a non-maintainer and a fork. In particular, confirm the permission lookup works with this job's limited token; if it doesn't, nothing runs.

## Checks
- **`actionlint`:** passes.
- **Patch handling:** a local test applied committed and new files, and the `.github/` check caught a file moved out of that folder.
- **`zizmor` (offline, so checks needing the GitHub API were skipped):** still reports findings, none suppressed:
  - **High, unpinned agent action:** item 1 above.
  - **High, `issue_comment` trigger:** needed for your feature; the checks above are the mitigation.
  - **Low, workflow concurrency:** deliberately set on the agent job, so unauthorized comments can't displace queued requests.
  - **`ci.yml`:** one low and one informational finding; I didn't edit that file.

## Also worth knowing
- **CI on agent commits:** pushes made with `GITHUB_TOKEN` generally don't start normal CI, as before. Don't treat the agent's commit as tested.
- **Trigger phrase:** every maintainer comment on a pull request still starts the agent, even "looks good". I'd require a prefix such as `/assistant`; I left it out because it changes how you use it.
- **Private organization members:** if a legitimate maintainer's run is skipped, the author-label pre-filter is the first thing to check.
- **Older checkout in CI:** `ci.yml` still uses `actions/checkout` v5.0.0; v7.0.1 is current. Dependabot would keep these pins up to date.

Nothing is committed or pushed.
