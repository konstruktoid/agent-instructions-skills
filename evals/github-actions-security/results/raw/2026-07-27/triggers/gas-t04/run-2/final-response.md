I'm unable to complete this — my current tool access in this session only includes Glob, Grep, Read, and Skill; there's no file-write or shell tool available to create `.github/dependabot.yml`. Could you enable write/edit (or Bash) access, or let me know if you'd like me to just paste the config here for you to add manually?

For reference, here's the minimal weekly config for GitHub Actions:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

Let me know how you'd like to proceed.
