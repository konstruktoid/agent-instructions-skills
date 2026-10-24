I added the release job to `.github/workflows/ci.yml` and rewrote the README's release section. I haven't run the workflow on GitHub.

**What changed in the workflow**
- **Triggers:** `ci.yml` now also runs on `v*` tag pushes. The `build` job still runs on pushes to main and on pull requests.
- **`release` job:** It runs only for `v*` tags, and only after `build` passes. It first checks that the tag equals `v` plus the `package.json` version. Then it runs `npm ci`, `npm run build` and `npm publish`, with `NPM_TOKEN` passed only to the publish step.
- **`github-release` job:** I made this a separate job, so the write token and the npm secret are never in the same job. It runs after `release` and creates the GitHub release for the tag with generated notes. It needs `contents: write`, and it does no checkout.
- **Hardening:**
  - Workflow permissions default to none, and each job gets only what it uses.
  - Actions are pinned to commit SHAs I looked up: `actions/checkout` v7.0.1 and `actions/setup-node` v7.1.0, the latest releases.
  - Checkout no longer persists credentials, every job has a timeout, and dependency caching is off.
  - I added concurrency control, and a release run is never cancelled.

**Checks**
- `actionlint` passes.
- `zizmor` (pedantic) reports one informational finding: it suggests npm trusted publishing instead of `NPM_TOKEN`. I kept the token because you asked for it, and I didn't suppress the finding.

**README:** The release section now describes the process: bump the version, merge, push a `vX.Y.Z` tag, and CI tests, publishes and creates the release.

**Still to do on your side**
- Confirm `NPM_TOKEN` is set as a repository secret. For tighter control, move it into a GitHub environment with required reviewers. I didn't, because that needs repository settings.
- The first real run is a tag push, which publishes to npm. I didn't push one.
- The repo has no `.github/dependabot.yml`, so the pinned SHAs won't update themselves. Adding one for `github-actions` would fix that.
