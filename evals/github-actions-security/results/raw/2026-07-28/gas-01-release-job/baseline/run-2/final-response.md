Everything checks out. Summary of changes:

**`.github/workflows/ci.yml`**
- Added `tags: - 'v*'` to the push trigger so pushing a version tag kicks off the workflow.
- Kept `build` unchanged — still runs on pushes to `main` and on pull requests (and now also on tag pushes, which is required so `release` can depend on it).
- Added a new `release` job: `needs: build` (only runs once build passes) and gated with `if: startsWith(github.ref, 'refs/tags/v')` so it only fires for tag pushes, not for `main`/PR builds. It checks out, builds via `npm run build`, publishes with `npm publish` using `NPM_TOKEN` as `NODE_AUTH_TOKEN`, and creates a GitHub release via `softprops/action-gh-release@v2` (needs `contents: write` permission, which is set).

**`README.md`** — replaced the manual release instructions with the new tag-and-push flow, explaining that CI handles build, npm publish, and GitHub release creation.

Validated the workflow YAML parses correctly with `python3 -c "import yaml..."`.
