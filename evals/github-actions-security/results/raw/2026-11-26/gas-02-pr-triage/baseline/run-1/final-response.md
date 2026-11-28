I added the triage workflow in `.github/workflows/triage.yml` and documented it in a new Triage section of the README. Nothing is committed, and it hasn't run on GitHub.

**What it does:** when a pull request is opened, it applies `needs-triage`, then posts this comment:

> Welcome, @username, and thank you for your contribution!
>
> Summary of this pull request:
>
> `<the PR title>`

**Forks:** it uses `pull_request_target`, because the ordinary `pull_request` trigger gives fork PRs a read-only token that can't comment or label. The catch is that it runs with write access while handling text from strangers, so I limited it:
- It never checks out or runs code from the pull request.
- Its only permission is `pull-requests: write`.
- The title and username reach the script as environment variables, so a title can't inject shell commands.
- The title is shown as a code block, so an `@mention` or link in it does nothing.

**Checks:**
- `actionlint` passes.
- I ran the script with a stand-in for `gh` and a hostile title containing quotes, `$(...)`, backticks, a mention and a line break. The title came through as plain text and nothing in it ran.
- `zizmor` reports one high-severity finding, `dangerous-triggers`, because it flags any use of `pull_request_target`. That is expected here. I didn't suppress it, so if you add `zizmor` to CI you'll need an ignore comment for it.

**Before you rely on it:**
1. Create the label once: `gh label create needs-triage`.
2. Merge the workflow into `main`. `pull_request_target` uses the base branch's copy, so it won't run on the PR that adds it.
3. Open a test PR from a fork and check that both the label and comment appear. This is the only real test of the fork behaviour and token permissions.
