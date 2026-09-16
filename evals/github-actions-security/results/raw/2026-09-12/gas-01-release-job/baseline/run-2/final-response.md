This looks correct: `build` runs on push (main + tags), and PRs; `release` runs only for `v*` tag pushes and only after `build` passes (`needs: build`), publishing to npm with `NPM_TOKEN` and creating a GitHub release via `softprops/action-gh-release`.

Files changed: `.github/workflows/ci.yml`, `README.md`.
