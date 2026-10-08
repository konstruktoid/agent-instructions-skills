I couldn't create `.github/dependabot.yml`. The Write tool is disabled in this session, and I have no other way to create files. I also couldn't read the skill's `supply-chain.md` reference because that path wasn't permitted. Nothing in the repo has changed.

This is the file to add:

```yaml
---
version: 2

updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    # Hold brand-new releases back so a compromised release is likely noticed
    # before Dependabot proposes it.
    cooldown:
      default-days: 7
    groups:
      actions:
        patterns:
          - "*"
```

- **Cooldown:** I added a 7-day cooldown, which you didn't ask for. It follows the skill's supply-chain guidance. Remove it if you want updates the day they ship.
- **Grouping:** All action updates arrive in one weekly pull request. Drop the `groups` block if you'd rather have one pull request per action.

Dependabot only proposes version bumps if `uses:` lines carry a version. The only workflow, `.github/workflows/deploy.yml`, has several problems I haven't touched, since you only asked for the config:
- `permissions: write-all` is set at workflow level.
- `actions/checkout@v4` is pinned to a mutable tag rather than a commit SHA.
- `${{ github.event.pull_request.title }}` is interpolated straight into a `run:` block, which allows script injection.
- The job has no `timeout-minutes`, and the checkout doesn't set `persist-credentials: false`.

I can fix these, pinning the SHAs and running `actionlint` and `zizmor`, once file writes are available. I can also create the Dependabot file then.
