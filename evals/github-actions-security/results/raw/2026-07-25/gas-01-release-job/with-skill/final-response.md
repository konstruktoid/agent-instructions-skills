This looks correct. I haven't pushed a tag to actually exercise the workflow (this is a change I'll flag as structural-only verification, not a live run).

## Summary

Added a `release` job to `.github/workflows/ci.yml`:
- Triggers on tags matching `v*` (added to the existing `on.push` trigger, alongside `main` and `pull_request`, which are unchanged).
- Gated with `needs: build` and `if: startsWith(github.ref, 'refs/tags/v')`, so it only runs after `build` passes on a tag push.
- Builds (`npm ci && npm run build`), publishes to npm via `npm publish` using `NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}`, then creates a GitHub release with `gh release create` using the built-in `GITHUB_TOKEN`.
- Follows the repo's security baseline: `permissions: {}` at workflow level with per-job scopes (`contents: read` for build, `contents: write` for release), actions pinned to commit SHAs (`actions/checkout` v7.0.1, `actions/setup-node` v7.0.0, both resolved live via `gh api`), `persist-credentials: false`, `timeout-minutes` on both jobs, and `package-manager-cache: false` to avoid zizmor's cache-poisoning warning since there's no lockfile to scope a cache key to.

Verification: `actionlint` clean; `zizmor --persona=pedantic` clean except one informational `use-trusted-publishing` finding, which I left as a documented deliberate exception (in-line comment) since the task specifically asked for NPM_TOKEN-based publishing rather than OIDC trusted publishing. The workflow wasn't actually run (no tag was pushed) — this is structural verification only.

Also updated the README's "Releasing" section to describe the new tag-push-triggered, CI-driven process instead of the old by-hand instructions.
