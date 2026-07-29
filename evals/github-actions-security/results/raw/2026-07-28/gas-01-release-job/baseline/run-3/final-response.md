YAML is valid. Summary of changes:

- `.github/workflows/ci.yml`: added `tags: v*` to the push trigger so the `build` job also runs on tag pushes; added a `release` job with `needs: build` and `if: startsWith(github.ref, 'refs/tags/v')` that installs deps, builds, `npm publish`s using `NPM_TOKEN` (via `NODE_AUTH_TOKEN`), and creates a GitHub release via `gh release create` using the default `GITHUB_TOKEN`. Top-level permissions are least-privilege (`contents: read`), with the release job explicitly elevated to `contents: write` only where needed.
- `README.md`: rewrote the "Releasing" section to describe the tag-push → CI → npm publish + GitHub release flow.
