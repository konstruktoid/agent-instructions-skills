I added `.github/dependabot.yml`, pinned all the action references to full commit SHAs, and replaced the README note with an explanation of how updates work now. Nothing is committed.

**Dependabot:** it checks GitHub Actions weekly and groups all updates, including major versions, into one pull request.

**Pins:** each reference now has the form `@<sha> # vX.Y.Z`, so Dependabot can update the SHA and the version comment together. I looked up the SHAs from the upstream tags and stayed within your current major versions:

| Action | Was | Now pinned to |
|---|---|---|
| `actions/checkout` | `v5` | `v5.1.0` |
| `astral-sh/setup-uv` | `v6` | `v6.8.0` |
| `github/codeql-action` (`init` and `analyze`) | `v3` | `v3.39.5` |

**README:** it covers the pinning format, the weekly grouped pull request, what to check when reviewing it, and how to add a new action.

**Checks:** the YAML parses, `actionlint` reported nothing, and `make lint test` passes (both targets only print a message). None of this runs the workflows or Dependabot on GitHub.

**What to expect after merging:**
- **Major upgrades:** newer majors already exist (checkout v7, setup-uv v10, CodeQL v4), so the first grouped pull request will probably include major jumps. Check the release notes for breaking changes. If one holds up the rest, you can limit the group to `minor` and `patch` with `update-types`, and majors will then arrive as separate pull requests.
- **CodeQL v3:** as far as I know, GitHub planned to deprecate it in December 2026, which is next month. I didn't verify that here, but I'd confirm it and move to v4 soon.
- **CodeQL isn't tested on pull requests:** `codeql.yml` only runs on its schedule, so an update to it is first exercised after merge. Adding a `workflow_dispatch` trigger would let you run it by hand. I didn't change any triggers.
