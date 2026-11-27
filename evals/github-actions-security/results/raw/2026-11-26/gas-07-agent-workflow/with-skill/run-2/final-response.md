I've rewritten `assistant.yml`, but **don't enable it on the public repository yet**: the agent action still isn't pinned. It has also never run on GitHub.

## What was wrong
The original let any commenter, on any pull request, drive an agent that had a `write-all` token and your model key. It also checked out fork code, and the checkout left the token in `.git/config`.

## What I changed

| Change | Why |
|---|---|
| Split into `authorize`, `change` and `push` jobs | The agent gets `contents: read`. It exports a patch, and a separate job applies and pushes it without running repository code. |
| Commenter must have `write`, `maintain` or `admin` access | There was no check at all. `author_association` is only a first filter. |
| `permissions: {}` by default, scopes set per job | Replaces `write-all`. |
| Removed `GH_TOKEN` from the agent step and set `persist-credentials: false` | The agent is no longer handed a credential that can write. |
| Checks out the head commit SHA resolved after authorization | The push fails if the branch has moved since then. |
| Deletes `CLAUDE.md`, `AGENTS.md`, `.mcp.json` and `.claude` before the agent runs | A branch can't reconfigure the agent. These files are also left out of the patch. |
| Push job refuses changes under `.github/` and to the default branch | Stops the agent editing automation or writing straight to your main line. |
| Triggers on `created` only | An edited comment could be someone else's text under the original author's name. |
| Added timeouts, one agent run per pull request, and the `assistant` environment | Limits cost and overlap, and gives the model key a narrower home. |
| Pinned `checkout` v7.0.1, `upload-artifact` v7.0.2 and `download-artifact` v8.0.2 | These are the newest releases I found, pinned to SHAs looked up today. |
| Added `zizmor.yml` | Ignores `dangerous-triggers` for this file, because the comment trigger is intentional. |

## Behaviour differences
Commenting still gets a change pushed to the pull request, with these exceptions:
- **Fork pull requests are refused.** `GITHUB_TOKEN` generally couldn't push to them anyway, and their code shouldn't run next to your key.
- **Editing a comment no longer re-runs it.**
- **The agent can't reply or call the GitHub API with your token.** If you relied on it posting comments, that needs adding back separately.
- **The agent is told not to commit or push.** The `push` job makes one commit as `github-actions[bot]`.

## Before you enable it
1. **Pin `acme/coding-agent`.** I couldn't resolve that repository (404 without logging in), so I didn't make up a SHA. If it's private or a placeholder, check its `action.yml`:
   - Does it accept this setup with no GitHub token?
   - Does it leave its edits in the workspace?
   - Can you restrict its tools? An unrestricted shell is the biggest remaining risk.
2. **Move `MODEL_API_KEY`** to an `assistant` environment limited to your default branch, and delete the repository-level secret. Adding required reviewers there gives you an approval step before each run.
3. **Protect branches** with rulesets, and set the repository's default token permission to read-only.

## Remaining risks
- **Key leakage:** the agent holds the model key and has network access. A prompt injection could send the key out, print it to the public log, or write it into the pushed files. Set a spending limit on the key. An egress allowlist would help, but I didn't add one because I don't know which hosts the agent needs.
- **Every maintainer comment starts a run**, including "LGTM". Requiring a prefix such as `/assistant` would fix that; I left it out to keep your behaviour.
- **CI probably won't run on the agent's commit**, because it's pushed with `GITHUB_TOKEN`. A GitHub App token for the push job would solve that.

## Checks
- **`actionlint`:** clean.
- **Shell steps:** in a scratch repository, the export and apply steps carried over edits, deletions, binary files and an agent-made commit. They left out the agent config files and rejected a `.github/` change.
- **Not tested:** the permission lookup, fork refusal, push, artifact handoff and agent action need a real run. Try a maintainer comment, a non-collaborator comment and a fork pull request in a private test repository. I gave `authorize` `contents: write` for the permission lookup; check whether `read` is enough.
- **`zizmor` (offline, pedantic):** not clean.

| Remaining finding | Status |
|---|---|
| High: `acme/coding-agent@v1` is unpinned | Yours to fix (step 1) |
| Low: no workflow-level concurrency in `assistant.yml` | Intentional, so unrelated comments can't displace a pending request |
| Low and informational: two findings in `ci.yml` | Existing file, not touched |

`ci.yml` also pins an older `checkout` (v5.0.0), worth updating separately. There's no Dependabot config to keep pins current.

Nothing is committed. While testing I also overwrote and then deleted `/tmp/sim.py`; I didn't check whether a file by that name already existed.
