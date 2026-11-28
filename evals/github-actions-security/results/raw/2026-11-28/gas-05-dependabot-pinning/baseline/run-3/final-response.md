I added `.github/dependabot.yml`, pinned the action references to commit SHAs and updated the README. The changes are uncommitted.

- **Dependabot:** it checks GitHub Actions weekly and puts all version updates, major ones included, into a single grouped pull request.
- **Pinning:** I replaced the major version tags with full commit SHAs plus a version comment. Dependabot updates both, and unlike a SHA, a tag can be moved to different code.

| Action | Was | Now pinned to |
|---|---|---|
| `actions/checkout` | `v5` | `fbc6f39…` (v5.1.0) |
| `astral-sh/setup-uv` | `v6` | `d0cc045…` (v6.8.0) |
| `github/codeql-action` (`init` and `analyze`) | `v3` | `74c1aea…` (v3.39.5) |

- **README:** it now explains the pin format, the weekly grouped pull request, what to check when reviewing it and how to add a new action.

I looked up the SHAs in the upstream repositories, and each matches what the old major tag points to today, so this doesn't change which action code runs. `actionlint` and YAML parsing passed, as did `make lint test`, though those targets only echo a message. Nothing has run on GitHub, so Dependabot's behaviour with this config is untested.

**What to expect next**
- **Major upgrades:** all three actions have newer major versions (`checkout` v7, `setup-uv` v10, `codeql-action` v4), so the first grouped pull request will probably be a large one. Read the release notes before merging.
- **CodeQL v3:** as far as I know, GitHub has scheduled v3 for deprecation in December 2026, which is next month. I didn't re-check that announcement. If it's right, move to v4 soon, either through Dependabot's pull request or by hand.
- **CodeQL testing:** that workflow only runs on its schedule, so pull request checks won't test CodeQL updates. Adding a `workflow_dispatch` trigger would let you run it by hand on the update branch; I didn't add one.
