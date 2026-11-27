I couldn't add the file: this session has no tool that can write files or run shell commands. The configuration below is ready to save as `.github/dependabot.yml`:

```yaml
---
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    cooldown:
      default-days: 7
    groups:
      github-actions:
        patterns:
          - "*"
    commit-message:
      prefix: "ci"
    labels:
      - "dependencies"
      - "github-actions"
```

- **`directory: "/"`**: Dependabot looks in `.github/workflows/` from this setting. It also checks action definitions in the repository root, such as an `action.yml`.
- **`cooldown`**: Dependabot waits 7 days after a release before proposing it. That gives time for a compromised or broken release to be noticed first.
- **`groups`**: all action updates arrive in one pull request each week, not one per action.
- **`labels`**: if the `dependencies` or `github-actions` labels don't exist in the repository, remove these lines. Otherwise Dependabot adds a comment to each pull request saying it couldn't apply them.

Dependabot will only update the `actions/checkout@v4` tag in `.github/workflows/deploy.yml` to newer tags. To get SHA pins, which it then keeps current, the workflow has to be pinned once with a tool like `pinact` or `ratchet`.

I haven't run `actionlint` or `zizmor` on this, and I couldn't open the security skill's guidance on Dependabot because permission to read it wasn't granted. Once the file is saved, GitHub validates it and reports any errors on the repository's Dependabot page.

**Problems in `deploy.yml`:** this is the only workflow in the repository, and it has serious security issues:
- **Line 7, `permissions: write-all`:** every job gets a token that can write to the repository. It should be `permissions: {}`, with each job granting only what it needs (likely `contents: read`).
- **Line 14:** `${{ github.event.pull_request.title }}` is pasted straight into the shell command, so a pull request title can run commands on the runner. The title should be passed through `env:` and used as `"$PR_TITLE"`.
- **Line 13:** `actions/checkout@v4` is pinned to a tag that can be moved, not a commit SHA. It also leaves out `persist-credentials: false`, so the token stays on the runner for later steps.
- **No `timeout-minutes`:** the job can run for the 6-hour default.

Do you want me to fix `deploy.yml` too, once file-writing access is available?
