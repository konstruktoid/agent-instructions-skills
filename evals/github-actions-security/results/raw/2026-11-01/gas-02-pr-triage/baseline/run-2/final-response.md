I added `.github/workflows/triage.yml` and a "Triage workflow" section in the README. I only checked that the workflow file parses as YAML. I haven't run it, because that needs a real pull request on GitHub.

- **What it does on open:** it comments "Welcome @author…" followed by `Summary: "<PR title>"`, and it applies `needs-triage`. It creates the label first if the repo doesn't have it.
- **Forks:** the workflow uses the `pull_request_target` trigger. The plain `pull_request` trigger gives a fork's PR a read-only token, so the comment and label would fail.
- **Why that trigger is safe here:** the workflow never checks out or runs code from the PR. The title and username reach the script through environment variables, not inline `${{ }}` expansion, so a malicious PR title can't inject shell commands.
- **Permissions:** the workflow is limited to `pull-requests: write` and `issues: write`, and it only uses the preinstalled `gh` CLI.
