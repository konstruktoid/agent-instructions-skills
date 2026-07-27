I've hit a hard constraint: this session's toolset doesn't include a file-editing tool (only Glob/Grep/Read/Skill), so I can't apply the change directly.

Here's what needs to change in `.github/workflows/deploy.yml`:

```yaml
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

replacing line 13 (`- uses: actions/checkout@v4`). That's the only third-party action reference in the repo — I searched for other `.github/workflows/*` and `action.yml`/`action.yaml` files and found none besides this one workflow.

Two caveats:
1. I couldn't run `gh api repos/actions/checkout/releases/latest` to confirm this is still the current release/SHA, since I have no command-execution tool available in this session — please verify before merging.
2. I left `permissions: write-all` and the unquoted `${{ github.event.pull_request.title }}` injection in the `run:` step untouched, since you only asked for the SHA pinning — let me know if you want those addressed too.

Can you grant file-edit access, or would you like me to proceed a different way (e.g., you apply that one-line diff yourself)?
