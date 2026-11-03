I added the Dependabot configuration, pinned every action to a commit SHA, and documented the update process in the README. I haven't committed anything.

**Dependabot** (`.github/dependabot.yml`):
- It checks the `github-actions` ecosystem weekly.
- All updates go into one pull request, through a single group that matches every action.
- It also has a 7-day cooldown, which you didn't ask for. It holds back brand-new releases so a malicious one has time to be caught.

**Pins:** the workflows used floating tags like `@v5`, which Dependabot can't keep current in the same way as pinned SHAs. I looked up the current releases today and pinned each action to its commit SHA with the version in a trailing comment:

| Action | Was | Now |
|---|---|---|
| `actions/checkout` | `@v5` | `v7.0.1` |
| `astral-sh/setup-uv` | `@v6` | `v10.3.2` |
| `github/codeql-action` (`init`, `analyze`) | `@v3` | `v4.39.1` |

- **`setup-uv`:** `v10.3.3` came out 4 days ago, inside the cooldown, so I used `v10.3.2`. Dependabot will move it forward once the cooldown passes.
- **Major-version jumps:** checkout (5 to 7), setup-uv (6 to 10) and codeql-action (3 to 4) are all major bumps. I didn't read their release notes for breaking changes. The workflows haven't run, so nothing confirms the new versions work with them. Check the first CI run, and mention the bumps in the pull request description.

**README:** it now explains the SHA pins, the weekly grouped pull request, the cooldown, and how to review those pull requests. It tells reviewers to read the upstream diff between the old and new SHAs before merging.

**Checks:** `actionlint` is clean. `zizmor` (pedantic) reports two low findings, both about missing workflow `concurrency` settings. They were already there and are outside this change, so I left them. I also added a short comment explaining the `security-events: write` permission in `codeql.yml`, which cleared a third finding.
