I hardened `.github/workflows/assistant.yml`, but **don't enable it on the public repo yet**: `acme/coding-agent@v1` still needs pinning to a commit SHA. The change is in your working tree, uncommitted.

## What was wrong
The most serious problem was that **anyone with a GitHub account could run it**. A comment from a stranger became the agent's instructions, with `MODEL_API_KEY` and a `write-all` token available to it. It also checked out the pull request's code, including code from forks, into that same privileged job.

## What I changed
| Change | Why |
|---|---|
| A new `gate` job checks that the commenter has admin or write access (maintain counts as write) | Only people who could push anyway can drive the agent |
| Fork PRs, closed PRs and PRs whose head is the default branch are refused | Keeps outside code away from your secrets, and keeps the agent from being pointed at `main` |
| Plain issue comments and bot comments are ignored | The workflow is for people commenting on PRs |
| The `edited` trigger is removed | Someone else with write access could edit a maintainer's comment and pass the author check |
| `write-all` became `contents: write` and `pull-requests: read`, on the agent job only | Least privilege |
| Checkout uses the PR's branch instead of `refs/pull/N/head` | The agent gets a real branch to push to, not a detached commit |
| `actions/checkout` is pinned to the SHA your `ci.yml` uses (I confirmed it is v5.0.0) | A tag can be moved |
| Added timeouts and one run per PR at a time | Limits runaway runs and push races |
| The prompt now says to push only to the checked-out branch | A guide for the agent, not an enforced limit |

## Verification
- `actionlint` passes.
- I ran the gate script against a stubbed `gh` for write, admin, read, no access, closed, fork, deleted fork and default-branch cases. All allowed or refused as intended.
- **Not tested:** a real run on GitHub, so neither the API calls nor the agent's push has been exercised.
- `zizmor` still reports two high findings:
  - **`unpinned-uses`:** this is real. I couldn't read `acme/coding-agent` without credentials, so I left a TODO rather than guess a SHA. Get the commit SHA for `v1`, review that code, and pin it.
  - **`dangerous-triggers`:** this is expected, since comment triggering is the feature. The gate is what mitigates it.

## Behaviour differences
- **Fork PRs no longer work.** The job's token generally can't push to a fork's branch anyway, but if you used the assistant on forks for anything else, that's gone.
- **Refusals are quiet.** The reason appears only as a notice in the Actions run.
- **Permissions are narrower.** If the agent also posts replies on the PR, it will now fail until you grant `pull-requests: write`.

## Before you turn it on
- **Protect `main` and release tags with rulesets.** `contents: write` isn't limited to one branch, and the prompt can't enforce that.
- **Prompt injection is still possible.** A maintainer might paste untrusted text into a comment, or the branch might contain merged outside content. The agent holds both the API key and a write token, so give the key a spending limit.
- **Every maintainer comment on a PR still starts the agent**, including "LGTM". I kept that to preserve behaviour; requiring a prefix such as `/assistant` is a small change I'd recommend.
- **The agent's pushes won't automatically run CI**, because they use the built-in token. Check those commits before merging.
- **Queued comments can be dropped.** Only one run waits per PR, so a third comment replaces the second.

A stronger next step is to give the agent a read-only token and have a separate job apply and push its patch. I didn't do that because it depends on whether `acme/coding-agent` can leave changes without pushing them, which I couldn't check.
