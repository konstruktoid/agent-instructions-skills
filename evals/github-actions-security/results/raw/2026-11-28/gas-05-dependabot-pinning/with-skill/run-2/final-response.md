I added `.github/dependabot.yml`, pinned all six action references to full commit SHAs, and documented the process in the README under "Action updates". Nothing is committed or pushed.

**Dependabot:** it checks GitHub Actions weekly and puts all updates, including major versions, into one pull request. I also added a 7-day cooldown, which you didn't ask for, so brand-new releases aren't proposed straight away. Remove the `cooldown` block (and its README line) if you don't want it.

**Pins:** Dependabot maintains SHA pins and their version comments, so I replaced the major-version tags and upgraded to current releases at the same time:

| Action | Was | Now |
|---|---|---|
| `actions/checkout` | `v5` | `v7.0.1` |
| `astral-sh/setup-uv` | `v6` | `v10.4.0` |
| `github/codeql-action` (`init`, `analyze`) | `v3` | `v4.39.4` |

`codeql-action` v4.39.5 exists but is only 4 days old, so I chose v4.39.4. Dependabot should propose the newer one once it clears the cooldown.

**Major-version changes to note in the pull request.** I checked the main release notes and changelog entries, not every intermediate release:
- **All three:** the versions now pinned run on Node 24. GitHub-hosted runners, which you use, handle this.
- **`checkout`:** v7 refuses to check out fork pull request code under `pull_request_target` and `workflow_run`. You use neither trigger.
- **`setup-uv`:** v7 and v8 changed inputs you don't set. v9 stops pruning the cache by default, so cache usage may grow. v10 turns off automatic caching for some sensitive events you don't use. It also no longer publishes major tags like `v10`.
- **`codeql-action`:** v3 is due to be deprecated in December 2026, so this move was needed soon anyway.

I also added a short comment explaining the `security-events: write` permission in `codeql.yml`.

**Checks**
- `actionlint` passes.
- Each SHA matches its release tag in the action's own repository.
- `zizmor` (pedantic, offline, so the checks that need the GitHub API didn't run) reports two low findings: neither workflow sets `concurrency`. That was already the case and would change how runs behave, so I left it.
- `make lint test` passes, though both targets only print a message.

**Not yet verified:** the upgraded actions haven't run on GitHub. Opening a pull request will exercise `ci.yml`. `codeql.yml` only runs on its Monday schedule and has no manual trigger, so check its first run after merging. Dependabot itself starts working once the file is on `main`.
