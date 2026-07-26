YAML is valid. Summary of changes:

- `.github/workflows/ci.yml`: added top-level `permissions: contents: read` (least privilege default), added `tags: - 'v*'` to the push trigger, and added a `release` job that `needs: build`, only runs when `github.ref` starts with `refs/tags/v`, gets its own `contents: write` permission (scoped only to that job), builds the package, publishes to npm using `NPM_TOKEN` via `NODE_AUTH_TOKEN`, and creates a GitHub release with `gh release create` using the built-in `GITHUB_REF_NAME`/`GITHUB_TOKEN` env vars (avoids interpolating ref data into the shell command).
- `README.md`: rewrote the Releasing section to describe the tag-push-triggered automated flow.

The existing `build` job is untouched in behavior — still runs on pushes to `main` and on pull requests (and now also on tag pushes, since `release` depends on it).
