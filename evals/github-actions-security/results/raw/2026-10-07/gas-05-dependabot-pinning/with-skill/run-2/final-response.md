I added a Dependabot config, pinned the action references to commit SHAs, and documented the update process in the README. Nothing is committed or pushed.

- **Dependabot:** `.github/dependabot.yml` checks the `github-actions` ecosystem weekly. A `groups` entry with pattern `*` puts all action updates into one pull request. I also added a 7-day cooldown so brand-new releases aren't proposed straight away.
- **Pinning:** Dependabot only updates SHA pins when each has its release in a trailing comment. I looked up the current releases and their commit SHAs with `gh api`, and none are written from memory. The jump to each latest release is a major-version bump:

  | Action | Was | Now |
  |---|---|---|
  | `actions/checkout` | v5 | v7.0.1 |
  | `astral-sh/setup-uv` | v6 | v10.2.0 |
  | `github/codeql-action` (`init`, `analyze`) | v3 | v4.38.2 |

  I did not read the release notes for the skipped versions. The workflows have not been run, so please check them before merging. `releases/latest` for `codeql-action` returned a `codeql-bundle` marker, so I took v4.38.2 from its tags and release list, where it is a published release from 2026-09-24.
- **README:** a new section says actions are SHA-pinned, Dependabot opens one weekly grouped pull request, and the cooldown applies. It also says to review the upstream diff rather than only the version number, and not to edit versions by hand.
- **Checks:** `actionlint` is clean. `zizmor` (pedantic, 1.29.0) reports 2 low findings, both about the workflows missing a `concurrency` setting. I left those alone because adding concurrency changes how runs behave and goes beyond what you asked for. I also added a comment on the `security-events: write` permission in `codeql.yml` to clear a third finding.
