I don't have a file-write or shell tool available in this session (only Glob, Grep, Read, and Skill), so I can't create `.github/dependabot.yml` directly. Here's the config to add — you can paste it in:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

This covers workflow files under `.github/workflows/` (Dependabot scans the whole repo for `uses:` references regardless of the `directory` value for this ecosystem). Let me know if you'd like me to also open a PR reviewing `deploy.yml` — I noticed it uses `permissions: write-all`, an unpinned `actions/checkout@v4`, and interpolates `github.event.pull_request.title` directly into a `run:` shell command, all of which the security skill flags as issues, but that's a separate change from what you asked for here.
