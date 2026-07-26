I don't have a file-write tool available in this session (only Glob/Grep/Read/Skill), so I can't create the file directly. Here's the config to add at `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

This covers actions referenced directly in `.github/workflows/*.yml`; Dependabot also picks up actions used inside any composite actions under `.github/actions/` automatically once this ecosystem is configured.

Separately, `.github/workflows/deploy.yml` has some notable issues unrelated to this request — `permissions: write-all`, an unpinned `actions/checkout@v4`, and unquoted interpolation of `github.event.pull_request.title` into a `run:` step (script injection risk). Let me know if you'd like me to fix those too.
