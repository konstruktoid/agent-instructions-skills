I added `.github/workflows/triage.yml` and a "Triage workflow" section in the README. I haven't run it. It needs a real pull request to test, and I didn't validate the YAML.

When a pull request is opened, the workflow:
- **Comment:** posts "Welcome, @username!", repeats the pull request title as a quoted line, and says a maintainer will triage it soon.
- **Label:** applies `needs-triage`, creating the label first if the repository doesn't have it.

**Fork support:** the workflow uses the `pull_request_target` trigger. A plain `pull_request` run from a fork gets a read-only token, so it couldn't comment or label. `pull_request_target` runs with a write token, so the workflow never checks out or runs code from the pull request. The job only calls the GitHub API, and the README warns to keep it that way.

**Untrusted input:** the title and username reach the script through environment variables, not `${{ }}` interpolation, so a crafted title can't inject shell commands.

**Token permissions:** the job has only `issues: write` and `pull-requests: write`.

**Actions:** it uses the preinstalled `gh` CLI instead of a third-party action, so there's no extra action to pin.

**Mentions in titles:** a title containing `@someone` will still ping that person, because the title is posted verbatim. Say if you want it neutralized, for example by putting it in a code span.
