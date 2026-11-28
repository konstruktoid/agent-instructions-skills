I added the Dependabot config, pinned every action to a full commit SHA, and documented the update process in the README. Nothing is committed yet.

**Changes**
- **`.github/dependabot.yml`:** checks `github-actions` weekly, with all version updates grouped into one pull request.
- **Workflows:** each `uses:` is now a SHA with a version comment, which Dependabot updates together.

  | Action | Was | Pinned to |
  |---|---|---|
  | `actions/checkout` | `v5` | v5.1.0 |
  | `astral-sh/setup-uv` | `v6` | v6.8.0 |
  | `github/codeql-action` (`init`, `analyze`) | `v3` | v3.39.5 |

- **`README.md`:** explains the pinning rule, the weekly grouped pull request and what to check when reviewing it.

Each SHA is the commit its major tag pointed to upstream when I looked, so pinning doesn't change which action code runs today.

**Checks:** `actionlint` reported nothing, the YAML parses, every `uses:` line matches the SHA-plus-version format, and the SHAs match the upstream release tags. `make lint` and `make test` pass, but they only echo messages. I haven't run the workflows or Dependabot on GitHub.

**Before you merge**
- **CodeQL v3 is due for retirement:** as I recall, GitHub announced that CodeQL Action v3 will be deprecated in December 2026, which starts within days. Please confirm that in GitHub's changelog. A v4 line already exists, so prioritise that upgrade.
- **The first Dependabot pull request will probably be large:** newer major versions exist for all three (checkout v7, setup-uv v10, CodeQL v4). Because they're grouped, one breaking change holds up the rest, so read the release notes before merging.
- **CodeQL updates aren't tested by pull requests:** `codeql.yml` only runs on its schedule. Adding `workflow_dispatch` would let you run it by hand after an update; I didn't change any triggers.
- **You lose some alerting:** GitHub doesn't raise Dependabot alerts for SHA-pinned actions. The README says so. Weekly version updates still run, but they aren't a substitute for security advisories.
