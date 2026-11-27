I hardened `.github/workflows/assistant.yml`, but **don't enable it on the public repository yet**: the agent action is still unpinned, and the workflow has never run on GitHub. It's the only file I changed, and nothing is committed.

## What was wrong
As written, **anyone with a GitHub account** could comment on a pull request and instruct an agent that had `write-all` permissions and your model API key. It checked out the PR's code, including code from forks, and left the write token in `.git/config`.

## What I changed

| Change | Why |
|---|---|
| Only commenters with write, maintain or admin access get through | There was no check on who was asking |
| Runs on new comments only, not edits or bot comments | Someone else can edit a maintainer's comment and re-trigger it; ignoring bots helps prevent loops |
| `write-all` replaced by per-job permissions | Each job gets only what it uses |
| Split into `authorize`, `agent` and `push` jobs | The agent now has a read-only token; the job that can write runs no agent or PR code |
| Fork PRs, closed PRs and the default branch are refused | Keeps outside code away from your key, and the agent's changes off `main` |
| Checks out an exact commit; the push fails if the branch has moved | Stops it overwriting newer work |
| Removes `CLAUDE.md`, `AGENTS.md`, `.mcp.json` and `.claude/` before the agent runs | A branch shouldn't be able to configure the agent working on it |
| Prompt marks the comment boundaries and says not to push | The later job does the push; the wording itself is not a security control |
| Added timeouts and one agent run at a time per PR | Limits cost and collisions |
| `actions/checkout` updated to v7.0.1, plus upload and download actions, all pinned by commit SHA | Tags can be moved |

## Behaviour differences
A maintainer can still comment and get a pushed commit, but:
- **Forks:** fork PRs are now rejected.
- **Agent access:** it can no longer push, comment or otherwise write to GitHub. If it used to reply on the PR, that stops.
- **Agent config:** it no longer sees the repository's `CLAUDE.md` or `AGENTS.md`, and its edits to those files or `.claude/` are dropped.
- **Workflow files:** changes under `.github/workflows/` can't be pushed with this token.
- **CI:** commits pushed this way don't start your CI, so check them before merging.

## Before you enable it
1. **Pin `acme/coding-agent`.** It returned 404 without a login, so it's private, nonexistent or a placeholder. I left `@v1` rather than invent a SHA.
2. **Read that action's source.** I couldn't, so I don't know whether it works with a read-only token and without pushing. I also couldn't restrict which tools or commands it may run; do that if it has an option for it.
3. **Set up the `assistant` environment.** Move `MODEL_API_KEY` into it and limit it to `main`. Required reviewers would add protection, at the cost of an approval click per run.
4. **Check repository settings.** Protect `main` with a ruleset, and make the default workflow token read-only.
5. **Test on a throwaway PR.** Confirm a maintainer's request gets pushed and a non-maintainer's is refused. The permission lookup in particular is untested.

## Remaining risks
- **The API key is still exposed to the agent.** Instructions hidden in repository files could make it leak the key through the network, the public log or the patch. Restricting outbound network access would reduce this; I didn't add it. Set a spending limit on the key.
- **A push just after the comment:** the commit is looked up when the run starts, so it could include something the maintainer hadn't seen.
- **Every maintainer comment on a PR still runs the agent**, as before. I recommend requiring a prefix such as `/assistant`; I didn't add it because it changes how people use it.

## Checks
- **`actionlint`:** clean.
- **Patch and push scripts:** in local test repositories, edits, new, deleted and binary files pushed correctly, and a moved branch was rejected.
- **`zizmor` (offline, pedantic):** not clean, and I suppressed nothing:
  - `unpinned-uses`: item 1 above.
  - `dangerous-triggers`: comment triggering is the feature you want to keep; the checks above are the mitigation.
  - Two low or informational findings are in `ci.yml`, which I didn't touch.
  - The other low one asks for workflow-wide concurrency. I limited only the agent job, so unrelated comments can't displace a queued request.
- **Action versions:** `gh` wasn't logged in, so I checked tags with `git ls-remote` and release dates with the public release feeds.
