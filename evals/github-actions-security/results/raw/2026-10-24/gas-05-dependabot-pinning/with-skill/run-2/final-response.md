I added a Dependabot config, pinned every action to a commit SHA, and documented the new update process in the README. I haven't committed anything or run the workflows.

**Dependabot** (`.github/dependabot.yml`): it checks the `github-actions` ecosystem weekly and groups all action updates into one pull request. I added a 7-day cooldown so brand-new releases are held back for a week.

**Action references**: tags are mutable and Dependabot can only maintain SHA pins that carry a version comment, so I replaced the tags with SHAs and comments. I resolved each release and SHA with `gh api`, not from memory.

| Action | Before | Now | Note |
|---|---|---|---|
| `actions/checkout` | `@v5` | `3d3c42e…` (v7.0.1) | Latest release. |
| `astral-sh/setup-uv` | `@v6` | `c18668a…` (v10.2.0) | v10.3.1 and v10.3.2 are only 2–3 days old, so the cooldown holds them back. v10.2.0 is the newest release that clears it. |
| `github/codeql-action` (init, analyze) | `@v3` | `6f2ac81…` (v4.39.0) | v4.39.1 is 3 days old, so I chose v4.39.0. This action publishes no usable GitHub releases, so I took the version from its tags. |

All three are major-version jumps (checkout 5→7, setup-uv 6→10, codeql-action 3→4). I didn't read their release notes for breaking changes. Look at those, and at the first CI run, before merging.

**README**: it now explains the SHA pinning, the weekly grouped pull request, the cooldown, and how to review those pull requests. The review guidance is to read the upstream diff between the old and new SHA and merge promptly. It also says new actions should be pinned to their latest release with a version comment.

**Checks**:
- `actionlint` is clean.
- `zizmor` (pedantic) reports 3 low findings, all unrelated to pinning: two missing workflow-level `concurrency` settings and one `permissions` entry without an explanatory comment. I didn't change these, since they are outside this task, and added no suppressions.
- The workflows haven't run. The changes are structural, but the major-version bumps mean behaviour is unverified until a CI run.
