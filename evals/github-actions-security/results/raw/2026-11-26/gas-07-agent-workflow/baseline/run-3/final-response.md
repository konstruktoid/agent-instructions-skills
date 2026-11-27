Checks are done: I linted the workflow and ran its shell steps locally. Here is the write-up.

I rewrote `.github/workflows/assistant.yml`, the only file changed (not committed). A maintainer can still comment on a PR and have the agent's change pushed to it. **Don't enable it on the public repo yet:** `acme/coding-agent` still needs pinning.

## What was wrong and what changed

| Problem | Fix |
|---|---|
| **Anyone could run the agent** by commenting, with your model key and a write-all token. This was the critical one. | A new `authorize` job requires the commenter to have write or admin access, and ignores bots. If the permission lookup fails, nothing runs. |
| `permissions: write-all` | Nothing by default; each job gets only what it needs. |
| The agent held a token that could write to the repo, so a prompt injection could misuse it. | Split into two jobs: `agent` is read-only and produces a patch, and `push` applies it without running the agent or any repo code. |
| It checked out fork code and ran the agent on it with secrets present. | Fork PRs are refused. |
| Comments on plain issues also triggered it. | Open pull requests only, and never when the PR's head is the default branch. |
| Editing a comment re-ran it, and the editor may not be the author. | Only new comments trigger it. |
| The branch could move between the request and the push. | The commit is fixed at authorisation, and the push fails if the branch has moved since. |
| Token left in the git config; `checkout` referenced by tag. | Credentials aren't persisted, and actions are pinned to commit SHAs. |
| No limits on run time or overlap. | Added timeouts and one agent run per PR at a time. |

## Behaviour differences
- **Pushing:** the prompt now tells the agent to edit files and not push. The workflow makes a single commit as `github-actions[bot]`, so any commit messages from the agent are lost.
- **Fork PRs:** they are now refused. The old workflow's `GITHUB_TOKEN` couldn't push to a fork anyway, though it could run the agent on one.
- **Edited comments:** to retry or correct a request, post a new comment.

## Before you enable it
1. **Pin `acme/coding-agent@v1`.** I couldn't read that repository (it asked for credentials), so I left a TODO rather than guess a SHA. Review the code at the commit you pin, since it receives `MODEL_API_KEY`.
2. **Check the agent works this way.** I couldn't run it. Confirm that it works with a read-only token, leaves its changes in the checked-out repository and doesn't fail when it can't push. Also check it doesn't leave scratch files there, because they would be committed.
3. **Protect your default and release branches.** The `push` job's token has `contents: write`, which isn't limited to the PR branch.
4. **Limit the model key.** The agent still holds it, and injected text in the repo or PR could try to leak it, including through the patch. Use a dedicated key with a spending cap. The prompt's "treat as data" line is not a security boundary.

## Worth knowing
- **Every maintainer comment still triggers a run**, as before, including ordinary review chat or quoting someone else's text. I'd require a prefix such as `/assistant`; it's a one-line condition, but it changes how you use it, so I didn't add it.
- **CI on the pushed commit:** a push made with `GITHUB_TOKEN` doesn't start your CI normally, which was also true before. Check it ran before merging, and read the agent's diff.
- **Limits of the push:** GitHub won't let this token push changes to workflow files. If the agent edits one, the whole push fails.
- **Replies and queuing:** the agent can no longer post PR comments. Refusals show only as notices in the run log. A newer request can replace one still waiting, and one that overlaps an earlier push may fail and need re-posting.

## Verification
- **`actionlint`:** passes.
- **`zizmor` (offline):** two high findings remain. One is the unpinned agent action above. The other flags the `issue_comment` trigger itself, which your feature needs and the permission check is there to guard.
- **Authorisation script:** with a stubbed `gh`, it allowed admin and write users. It refused read and no-access users, closed PRs, forks and the default branch, and failed on a lookup error.
- **Patch and push scripts:** against a local repository, committed, deleted and new binary files all came through, and a push to a moved branch was rejected.

Nothing has run on GitHub itself, so try one request on a test PR first.
