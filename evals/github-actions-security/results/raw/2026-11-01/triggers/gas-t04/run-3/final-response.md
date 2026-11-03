I couldn't create the file: this session has no file-writing or shell tool, only read and search. Save the following as `.github/dependabot.yml`:

```yaml
---
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"            # covers .github/workflows/ (and action.yml at the root, if added)
    schedule:
      interval: "weekly"
      day: "monday"
    cooldown:
      default-days: 7         # wait a week after a release so a compromised one has time to be spotted
    groups:
      github-actions:
        patterns:
          - "*"               # one weekly PR for all action bumps instead of one per action
    commit-message:
      prefix: "ci"
    labels:
      - "dependencies"
      - "github-actions"
```

- **Weekly with a cooldown:** Dependabot opens update PRs every Monday. It skips any release that came out less than 7 days ago, which gives time for a malicious release to be caught.
- **Grouped:** all action updates arrive as one PR instead of one per action. Remove the `groups` block if you'd rather review them one at a time.
- **Labels:** Dependabot only applies labels that already exist in the repo. Create `dependencies` and `github-actions` first, or delete the `labels` block.
- **Not checked:** I didn't run any validation. GitHub checks the file when it's pushed to the default branch, and you can see the result under Insights → Dependency graph → Dependabot.

### Problems in `.github/workflows/deploy.yml`

I didn't change this file because you didn't ask me to, but it has serious security problems:

1. **Command injection, line 14:** `${{ github.event.pull_request.title }}` goes straight into `run:`. Anyone who can open a PR can run shell commands by putting them in the PR title. Pass the title through `env:` and print it with `printf '%s\n' "$PR_TITLE"`.
2. **Too many permissions, line 7:** `permissions: write-all` on a `pull_request` trigger. Change it to `permissions: {}` at workflow level, and give the job only `contents: read`.
3. **Action pinned by tag, line 13:** Dependabot will keep `actions/checkout@v4` updated, but a tag can be moved to different code. Pin it to a full commit SHA with the version in a comment. Dependabot keeps SHA pins and their comments up to date too.
4. **Missing settings:** `actions/checkout` has no `persist-credentials: false`, and the job has no `timeout-minutes`.

Also, a job called `deploy` that runs on every pull request is a design problem in itself. Deployments usually run on `push` to the main branch or on a release.

Want me to fix `deploy.yml` too? I'd need file-writing access in this session.
