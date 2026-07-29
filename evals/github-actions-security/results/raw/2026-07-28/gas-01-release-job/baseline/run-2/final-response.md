This looks correct and complete. Summary of the design:

- **Trigger**: `push` now includes `tags: ['v*']` alongside the existing `main` branch push, plus `pull_request` unchanged.
- **`build` job**: unchanged behavior — runs on pushes to `main`, on PRs, and now also on tag pushes (needed so `release` has something to depend on for the tag event).
- **`release` job**: `needs: build` (won't start until build passes) and gated with `if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')` so it never runs for `main` pushes or PRs — only tag pushes. It builds, publishes to npm via `NODE_AUTH_TOKEN: secrets.NPM_TOKEN`, and creates a GitHub release via `gh release create` using the built-in `GITHUB_TOKEN`.
- **Least privilege**: added a top-level `permissions: contents: read`, with `contents: write` scoped only to the `release` job (needed to create the release), so the `build` job — which also runs on untrusted PR code — doesn't get write access.

README's release section now documents the tag-and-push flow instead of manual publishing.
