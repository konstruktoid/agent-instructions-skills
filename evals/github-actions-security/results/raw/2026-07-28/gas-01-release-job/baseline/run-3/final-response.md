This is a small, already-completed change (two file edits, verified via YAML lint) — no task tracking needed.

## Summary

Added a `release` job to `.github/workflows/ci.yml`:
- Workflow now also triggers on pushes of tags matching `v*` (build still runs on `main` pushes and PRs as before).
- `release` job uses `needs: build` so it only runs after `build` passes, and `if: startsWith(github.ref, 'refs/tags/v')` so it only fires for tag pushes (not PRs or main pushes).
- It builds the package, publishes to npm via `npm publish` using `NPM_TOKEN` as `NODE_AUTH_TOKEN`, and creates a GitHub release with `gh release create` (avoids pulling in a third-party release action).
- Added top-level `permissions: contents: read` with `contents: write` scoped only to the `release` job (least-privilege; the `build` job needs no secrets or write access, including for PR runs from forks).

Updated the README's "Releasing" section to describe tagging with `v*` and the automated CI flow instead of manual publishing.
