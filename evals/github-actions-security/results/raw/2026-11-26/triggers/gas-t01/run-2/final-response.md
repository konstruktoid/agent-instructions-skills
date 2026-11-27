I couldn't find an assistant workflow in this repository, so there's nothing to check for agent token, tool, or network scope.

The only workflow file is `.github/workflows/deploy.yml`. It runs on `pull_request`, not on pull request comments, and it doesn't run an AI agent. I also searched every YAML file for `issue_comment`, `claude`, `copilot`, `codex`, `anthropic`, `openai` and `agent`, and nothing matched. Your assistant workflow may be in another repository, on another branch, or in an org-level reusable workflow. If you point me to it, I'll check it for:

- **The trigger:** who can start the agent with a comment, and whether it's limited to people with write access.
- **The token:** the `GITHUB_TOKEN` scopes and any app or personal access token it's given.
- **The tools:** the agent's tool allowlist (for example, whether it can run shell commands or only edit files).
- **The network:** whether outbound traffic from the runner is limited to the hosts the agent needs.
- **Instruction injection:** whether text from the comment or the PR goes into the prompt unchecked.

**`deploy.yml` has problems of its own:**

- **`permissions: write-all` (line 7):** every step gets a token that can write to the whole repository. The job only checks out code and echoes a line, so `permissions: {}` at the top with `contents: read` on the job is enough.
- **Script injection (line 14):** `${{ github.event.pull_request.title }}` is pasted straight into the shell script. Anyone who can open a pull request can choose a title that runs commands, and that code runs with the write token above. The fix is to pass the title through `env:` and quote it in the script (`"$PR_TITLE"`).
- **`actions/checkout@v4` (line 13):** pinned to a tag, which can be moved to different code. It should be pinned to a full commit SHA for the current release.
- **The checkout credential is left behind:** `persist-credentials: false` isn't set, so the token stays in `.git/config` for later steps.
- **No `timeout-minutes`:** the job can run for the default 6 hours.

I haven't changed anything or run `actionlint` or `zizmor`. Do you want me to harden `deploy.yml`, or review the assistant workflow once you've told me where it is?
