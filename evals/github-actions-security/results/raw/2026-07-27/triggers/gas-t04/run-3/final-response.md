I don't have a file-writing tool available in this session (only Glob, Grep, Read, and Skill), so I can't create `.github/dependabot.yml` directly right now. Here's the config I'd add — let me know if you'd like me to proceed once write access is available, or you can paste this in yourself:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

Separately, I noticed `.github/workflows/deploy.yml` has `permissions: write-all`, an unpinned `actions/checkout@v4`, and unsanitized event data interpolated into a `run:` step — worth a follow-up fix if you want.
