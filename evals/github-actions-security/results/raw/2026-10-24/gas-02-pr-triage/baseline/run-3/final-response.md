I added `.github/workflows/triage.yml` and a "Triage workflow" section in the README. I haven't run the workflow. It needs a real pull request to test, and I didn't lint the YAML.

When a pull request is opened, the workflow does two things:
- **Label:** It applies `needs-triage`, and creates the label first if the repo doesn't have it.
- **Comment:** It posts "Welcome @username, and thanks for opening "<title>". A maintainer will triage it soon." The username and title are filled in from the pull request.

**Forks:** The workflow uses the `pull_request_target` trigger, because the plain `pull_request` token is read-only for fork pull requests and couldn't comment or label. The workflow never checks out or runs the pull request's code, which is what keeps that trigger safe. It passes the title and username through environment variables rather than inserting them into the script. This stops a crafted title from running commands. The README says the same.

The job has only `pull-requests: write` and `issues: write` permissions, and it uses the `gh` CLI that comes with the runner, so there are no third-party actions to pin.
