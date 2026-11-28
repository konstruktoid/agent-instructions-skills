I added `.github/workflows/triage.yml` and a "Pull request triage" section in the README. Nothing is committed.

**What it does:** when a pull request is opened, it applies `needs-triage`, then posts a comment that greets `@username` and repeats the title.

**Fork support:** it uses `pull_request_target`, because the ordinary `pull_request` token is read-only for forks and couldn't comment or label. That trigger is risky if misused, so:
- It never checks out or runs code from the pull request.
- Its only permission is `pull-requests: write`.
- The title and username reach the script as environment variables, so a crafted title can't run commands.
- The title appears in a code block, so it can't ping people or add links in the bot's name. It will look like quoted text rather than prose.

**Checks:**
- I ran both scripts locally with a fake `gh` and a title containing shell commands, mentions, Markdown and a line break. The title was passed through as plain text and nothing in it ran.
- `actionlint` passed.
- `zizmor` reports one high finding, `dangerous-triggers`, which flags any use of `pull_request_target`. It's expected here, and I left it visible rather than suppressing it. If your CI enforces `zizmor`, you'd need to add an ignore comment.

I haven't tested it on GitHub, so the real API calls and fork permissions are unconfirmed.

**Before you rely on it:**
1. Create the `needs-triage` label in the repository.
2. Merge the workflow into `main`. `pull_request_target` uses the base branch's copy, so the pull request that adds it won't be triaged.
3. Open a test pull request from a fork and check that both the label and the comment appear.
