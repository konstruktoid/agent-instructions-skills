I couldn't create `.github/dependabot.yml`. The Write tool is disabled in this session, so nothing in the repo has changed. I also couldn't read the skill's `supply-chain.md` reference because the read wasn't permitted. The cooldown below is therefore my own choice, not something I checked against that file. I haven't run `actionlint` or `zizmor` either, since there was no file to check.

This is the file I would add at `.github/dependabot.yml`:

```yaml
version: 2

updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    # Wait before adopting a new release so a compromised one is likely noticed first.
    cooldown:
      default-days: 7
    groups:
      github-actions:
        patterns:
          - "*"
```

- **Weekly:** `interval: weekly` runs the check once a week.
- **Cooldown:** a new release has to be 7 days old before Dependabot proposes it.
- **Grouping:** all action updates arrive in one pull request.
- **Scope:** `directory: /` makes Dependabot scan `.github/workflows/`.

I can write the file if you enable Write or tell me another way to create it.

I also noticed some problems in `.github/workflows/deploy.yml`. I haven't touched them, since you only asked about Dependabot:
- **Over-broad permissions:** `permissions: write-all` is set on a `pull_request` workflow.
- **Script injection:** `${{ github.event.pull_request.title }}` is interpolated directly into a `run:` block. The title should go through `env:` instead.
- **Unpinned checkout:** `actions/checkout@v4` is a mutable tag. It should be pinned to a commit SHA, and Dependabot can then keep that SHA current.
- **Missing safeguards:** the job has no `timeout-minutes`, and the checkout doesn't set `persist-credentials: false`.

Want me to fix those too?
