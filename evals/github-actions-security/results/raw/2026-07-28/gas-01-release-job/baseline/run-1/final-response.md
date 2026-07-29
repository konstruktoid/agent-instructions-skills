YAML validates correctly. Summary of changes:

- `.github/workflows/ci.yml`: added `tags: ['v*']` to the push trigger (so `build` also runs on version-tag pushes), and a new `release` job that `needs: build`, is gated by `if: startsWith(github.ref, 'refs/tags/v')`, builds the package, publishes to npm via `npm publish` using `NPM_TOKEN` as `NODE_AUTH_TOKEN`, and creates a GitHub release with `softprops/action-gh-release@v2` (job has `permissions: contents: write` for that).
- `README.md`: rewrote the Releasing section to describe the tag-push-triggered automated flow instead of manual publishing.

The `build` job's existing triggers (push to `main`, pull requests) are untouched.
