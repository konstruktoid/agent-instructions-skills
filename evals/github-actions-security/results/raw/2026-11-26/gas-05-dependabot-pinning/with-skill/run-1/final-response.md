I added `.github/dependabot.yml`, pinned every action to a commit SHA and added an "Action updates" section to the README. Nothing is committed, and the updated workflows have not run on GitHub.

**Dependabot** checks GitHub Actions weekly and groups all version updates, including major ones, into one pull request. I also added a 7-day cooldown, which you didn't ask for, so brand-new releases aren't adopted immediately. Security updates, if enabled, arrive as separate pull requests.

**Action references** are now full commit SHAs with a version comment, which Dependabot updates together. I matched each SHA against its upstream release tag.

| Action | Before | After | Newer release held back by the cooldown |
|---|---|---|---|
| `actions/checkout` | `v5` | `v7.0.1` | none |
| `astral-sh/setup-uv` | `v6` | `v10.3.3` | `v10.4.0` (published Nov 20) |
| `github/codeql-action` (`init`, `analyze`) | `v3` | `v4.39.3` | `v4.39.4`, `v4.39.5` |

**Major version changes** to note in the pull request description. I read selected release and changelog notes, not every skipped release.
- **`checkout`:** v6 stores the persisted credential in a separate file. v7 blocks checking out fork pull requests under `pull_request_target` and `workflow_run`. Your workflows use neither trigger and already disable credential persistence.
- **`setup-uv`:** it now runs on Node 24 and no longer prunes the cache by default, so cache usage may grow. v7 and v8 removed or changed the `server-url` and `manifest-file` inputs, which you don't use. v8 also stopped publishing major tags such as `@v8`.
- **`codeql-action`:** v4 runs on Node 24, and recent releases raise the minimum CodeQL bundle version. Your workflow doesn't set a bundle version.

**Checks**
- `actionlint` is clean, and `make lint test` passes locally.
- `zizmor` 1.31.1, run offline, reports nothing at its default level (3 findings suppressed).
- At the pedantic level it still reports 3 low findings: no `concurrency` setting in either workflow, and no comment explaining `security-events: write`. These were outside this task, so I left them.

**Still to verify**
- Opening a pull request will exercise `ci.yml`.
- `codeql.yml` only runs on its Monday schedule, so check the first run after merging.
- Dependabot starts only once the file is on the default branch.

**Noticed but not changed**
- `codeql.yml` analyses `python`, but the repository has no Python files, so that job is likely to fail regardless of this change.
- `setup-uv` still installs the latest `uv` at run time, which SHA pinning and this Dependabot configuration don't control. The current `make test` doesn't use `uv` at all.
