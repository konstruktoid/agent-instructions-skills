Checks are done: the only lint errors left are the two I expected. I'm writing up the results now.

I rewrote `.github/workflows/assistant.yml`. A maintainer can still comment on a PR and have the change made and pushed, with some new limits. **Don't enable it yet:** the agent action still needs pinning, and I couldn't check how it behaves.

## What was wrong
- **Anyone could run it.** Any GitHub account could comment and direct an agent that had `write-all` permissions and your model API key. This was the critical problem.
- **It ran fork code with those secrets.** It checked out the PR head, so a stranger's files could steer or hijack the agent.
- **Other gaps:** it also ran on plain issues and on edited comments, used movable action tags, and had no timeout.

## What I changed
| Change | Why |
|---|---|
| Only users with `write` or `admin` access, checked through the API | `author_association` also matches org members and collaborators who can't write |
| Only new comments from human users, on PRs | Blocks edited comments, bots and plain issues |
| Open, same-repository PRs only, never with the default branch as head | Keeps outside code away from the secrets |
| The commit is fixed when the permission check runs | The agent and the push use the same commit |
| The agent job is read-only and hands over a patch; a separate job pushes it | A manipulated agent never holds a token that can write to the repo |
| The push job rejects changes under `.github/` | Stops the agent from altering workflows or local actions |
| The push fails if the branch has moved | Nobody's newer commits or rewinds get overwritten |
| `checkout` and the artifact actions pinned to commit SHAs; timeouts and per-PR queueing added | Limits supply-chain and runaway-job risk |

## Behaviour differences
- **Fork PRs are now skipped.** `GITHUB_TOKEN` generally can't push to a fork anyway, but the agent could previously still run on one.
- **The agent can no longer push or post comments itself.** The workflow commits as `github-actions[bot]`. If you relied on the agent replying on the PR, that needs a separate step.
- **Skipped requests show only a notice in the run log**, not on the PR.

## Testing
- `actionlint` passes.
- I ran the permission check against a fake `gh`: write and admin were allowed; read, no access, fork and default-branch cases were skipped.
- I ran the patch and push scripts on local Git repositories. Normal, binary and agent-committed changes were pushed. `.github/` edits and moved or deleted branches were rejected, and an empty patch did nothing.
- The workflow has **not run on GitHub**, and the real agent was never run.

## Before you enable it
1. **Pin `acme/coding-agent`.** I couldn't access its repository, so it's still `@v1`. Review it and pin a full commit SHA.
2. **Confirm it works this way.** It must leave its edits (or local commits) in the checked-out directory, and cope with a read-only `GH_TOKEN`. If it only writes through the GitHub API, this design needs adjusting.
3. **Limit the API key.** The agent can still read `MODEL_API_KEY` and has network access, so use a dedicated key with a spending cap. Treat text a maintainer quotes from others, and files on the branch, as possible prompt injection.
4. **Review what it pushes.** Blocking `.github/` doesn't stop harmful edits to code, the `Makefile` or other files that run later. Keep branch protection and required review on the default branch.
5. **Check CI on agent commits.** Pushes made with `GITHUB_TOKEN` generally don't start CI automatically, so you may need to trigger it yourself.

`zizmor` still reports two errors: the unpinned agent action, and the `issue_comment` trigger. The trigger is needed for comment commands, and the permission check is what guards it.

**One option I didn't apply:** every comment from a maintainer still runs the agent, even "looks good". Requiring a prefix such as `/assistant` would fix that, but it changes how you use it. Also, if several comments arrive while a run is in progress, only the newest waiting one is kept.

The changes are uncommitted in your working tree.
