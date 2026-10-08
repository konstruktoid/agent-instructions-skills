I added `.github/workflows/triage.yml` and a "Triage workflow" section in the README. I haven't run it. It only fires on a real pull request, and I didn't validate the YAML.

When a pull request is opened, the workflow creates the `needs-triage` label if it's missing and applies it. It also posts this comment: `Welcome @<author>, and thanks for opening "<title>". A maintainer will triage it soon.`

- **Forks:** the workflow uses the `pull_request_target` trigger. The plain `pull_request` trigger gives fork PRs a read-only token, so the comment and label would fail. `pull_request_target` runs with write access, so the workflow never checks out or runs code from the PR. The permissions are limited to `issues: write` and `pull-requests: write`.
- **Untrusted text:** the PR title and username reach the shell through environment variables, not `${{ }}` inside the script. A title containing shell syntax can't run as a command.
- **No third-party actions:** it uses the preinstalled `gh` CLI, so there are no action versions to pin.

I left `ci.yml` as it was.
