Everything's in order. Summary of the work:

**`.github/workflows/ci.yml`**
- Added `permissions: {}` at the workflow level and a `concurrency` group.
- `build` job: unchanged trigger behavior (push to `main`, pull requests), now also runs on tag pushes (needed to gate the release); pinned `actions/checkout` and `actions/setup-node` to their latest release SHAs (`v7.0.1`, `v7.0.0`), `persist-credentials: false`, `timeout-minutes: 10`, `contents: read`.
- New `release` job: `needs: build`, gated with `if: startsWith(github.ref, 'refs/tags/v')` so it only fires on `v*` tag pushes and only after `build` passes; builds via `npm ci && npm run build`, publishes with `npm publish` using `NPM_TOKEN` via `NODE_AUTH_TOKEN`, and creates the GitHub release with `gh release create` using the built-in `GITHUB_TOKEN` (scoped to `contents: write`, commented why).
- Disabled `setup-node`'s built-in package-manager caching (`package-manager-cache: false`) in both jobs to close a cache-poisoning path into the release job, per zizmor's finding.

**README.md** — rewrote the "Releasing" section to describe the new tag-push-triggered, CI-driven flow.

**Verification** — `actionlint` clean; `zizmor --persona=pedantic` reduced from 5 findings (2 high, 1 low, 1 info, plus a documentation gap) down to a single informational finding (`use-trusted-publishing`), which is a deliberate, commented exception since the task requires the static `NPM_TOKEN` approach rather than OIDC trusted publishing. I could not trigger a live workflow run — the repo has no configured git remote — so this is verified structurally (linting/security audit) but not by an actual Actions run; flagging that limitation as instructed.
