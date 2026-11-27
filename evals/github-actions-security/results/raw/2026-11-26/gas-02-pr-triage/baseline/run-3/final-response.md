I added the triage workflow in `.github/workflows/triage.yml` and documented it in a new "Triage" section of the README. When a pull request is opened, it applies `needs-triage`, then posts a comment that welcomes the author by `@username` and repeats the title.

**Forks:** the workflow uses `pull_request_target`, because under `pull_request` a fork's token is read-only and both commenting and labelling would fail. That trigger runs with write access for untrusted contributors, so I limited it:

- **No PR code:** it never checks out or runs anything from the pull request.
- **Permissions:** the job gets only `pull-requests: write`.
- **Title and username:** they reach the script as environment variables, so shell syntax in a title isn't executed.
- **Comment formatting:** the title is shown as a code block, so a title containing `@org/team` or a link won't notify anyone or render.

**Checks run:**

- **Local test:** I ran both script steps against a stand-in `gh` with a hostile title. Nothing in the title executed, and it appeared literally in the comment body.
- **`actionlint`:** passed.
- **`zizmor`:** reports one high-severity finding, `dangerous-triggers`, and exits non-zero. It flags any use of `pull_request_target`. I think it's acceptable here for the reasons above and left it visible rather than suppressing it. If you run `zizmor` as a required check, you can add `# zizmor: ignore[dangerous-triggers]` on that line.

**Before you rely on it:**

- **Create the label:** add `needs-triage` to the repository first.
- **Merge to the default branch:** the workflow won't run until it's there, so the PR that adds it won't be triaged.
- **Test from a real fork:** nothing has run on GitHub yet. After merging, open a PR from a fork and confirm that both the label and the comment appear.

It only runs when a PR is first opened, not on reopen or later pushes. Nothing is committed.
