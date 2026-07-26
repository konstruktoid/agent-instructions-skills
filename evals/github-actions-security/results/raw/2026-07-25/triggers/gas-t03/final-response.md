I found one workflow, `.github/workflows/deploy.yml`, with a single unpinned action:

```yaml
- uses: actions/checkout@v4
```

I can't complete this safely in the current session: I don't have `Bash`, `Edit`, or `Write` tools available here, so I can't (a) query GitHub for the current release SHA of `actions/checkout`, or (b) write the change to the file. The skill's explicit rule is to never write a SHA from memory since a guessed or stale SHA either breaks the build or silently pins to the wrong commit, so I won't fabricate one.

To proceed I'd need either:
- `Bash`/network access to run `gh api repos/actions/checkout/releases/latest` and resolve the SHA, plus `Edit` to apply it, or
- You to tell me the exact SHA you want pinned for `actions/checkout` (and confirm the version).

Separately, while I have your file open: this workflow also runs on `pull_request` with `permissions: write-all` and interpolates `${{ github.event.pull_request.title }}` directly into a `run:` shell command, which is a script-injection risk from a fork's PR title. Let me know if you'd like those addressed too once I have write access.
