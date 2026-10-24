I've hardened `.github/workflows/assistant.yml`. I haven't run it, so it's untested. The change is uncommitted in the working tree.

**What was wrong and what I changed**

1. **Anyone could trigger it.** `issue_comment` fires for every commenter, and on a public repo that means anyone with an account. They would get an agent holding your model key and a write token. The job now runs only if the commenter's `author_association` is `OWNER`, `MEMBER` or `COLLABORATOR`.
2. **It ran on plain issues as well as PRs.** The job now also requires `github.event.issue.pull_request`.
3. **Any maintainer comment started it.** I added a `startsWith(comment.body, '/assistant')` condition so only a deliberate invocation runs. This changes behaviour slightly: maintainers now need to start their comment with `/assistant`. Remove that line if you'd rather keep it open.
4. **`permissions: write-all`.** I replaced it with an empty workflow-level default. The job gets only `contents: write` (to push) and `pull-requests: write`.
5. **Fork PRs would run untrusted code next to the secrets.** The workflow checked out `refs/pull/N/head`. For a fork PR that is attacker-controlled content, in a job holding `MODEL_API_KEY` and a write token. A new first step looks up the PR's head repo and fails unless it is this repository. The agent can't push to forks anyway, so you lose nothing.
6. **Edited comments replayed the trigger.** I removed the `edited` event, so changing an old comment can't re-run the agent. Only `created` triggers it now.
7. **Smaller fixes.**
   - A `concurrency` group per PR, with no cancellation, stops two agents pushing at once.
   - `timeout-minutes: 15` limits a runaway agent.
   - I dropped the odd `issue.number && format(...)` checkout expression, since the `if` condition already guarantees a PR.
   - I use `github.token` instead of `secrets.GITHUB_TOKEN`; they're equivalent.

**Things I left alone, and what you should still do**
- **Pinning:** `acme/coding-agent@v1` and `actions/checkout@v5` are tag-pinned. For a job with secrets, pin both to full commit SHAs. I couldn't look up the SHAs from here.
- **Comment text in the prompt:** it still goes into the prompt, which is the behaviour you wanted. That's now acceptable only because the commenter is a trusted maintainer. The agent can still be steered by content in the PR itself, such as files or the description.
- **Token on disk:** the checkout still persists the token, because the agent needs it to push. Check that `acme/coding-agent` doesn't expose it.
- **Branch protection:** require review and status checks on `main`. The agent pushes to PR branches, not `main`, but it can still alter workflow files in the PR. The `GITHUB_TOKEN` can't modify `.github/workflows` without the `workflows` permission, which I haven't granted.
- **Environment secret:** consider storing `MODEL_API_KEY` in a protected environment.
