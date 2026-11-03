I added the release jobs to `.github/workflows/ci.yml` and rewrote the README's release section. I haven't pushed anything or run the workflow, so the release path is untested on a runner. `actionlint` is clean. `zizmor` (pedantic) has one remaining informational finding, which is expected (see below).

**Workflow**
- **Triggers:** `v*` tags are now a trigger alongside pushes to `main` and pull requests. The `build` job still runs on all of them.
- **`publish` job:** it runs only on a `v*` tag push, and only after `build` passes.
  - It checks that the tag equals `v` plus the `package.json` version, then runs `npm ci` and `npm run build`.
  - It publishes with `npm publish`, passing `NPM_TOKEN` to that step only.
  - It has no dependency cache, and its `GITHUB_TOKEN` is read-only.
- **`github-release` job:** it runs after `publish` and creates the release with `gh release create --verify-tag --generate-notes`. It is the only job with `contents: write`, and it runs none of the repository's code.
- **Hardening:**
  - Workflow permissions default to none, and each job grants its own.
  - Both actions are pinned to the latest release, looked up now: `actions/checkout` v7.0.1 and `actions/setup-node` v7.1.0. Both are older than 7 days.
  - Checkout no longer keeps the token, every job has a timeout, and the tag name goes through `env:`.
  - A concurrency group stops a release run from being cancelled.
- **Major version bumps:** the existing workflow used v4 of both actions. In `actions/setup-node` v7, `NODE_AUTH_TOKEN` is no longer set to a dummy value. I pass it explicitly in the publish step, so this doesn't affect the workflow. I also set `package-manager-cache: false` so setup-node's automatic caching is off.

**Things to know**
- **Remaining `zizmor` note:** it prefers npm trusted publishing (OIDC) over a stored token. I kept `NPM_TOKEN` because you asked for it. Trusted publishing would remove the stored secret if you want to switch later.
- **Missing files:** the repo has no `package-lock.json` and no `build.js`. `npm ci` and `npm run build` will fail until those are committed. The existing `build` job already needed the lockfile.
- **Optional setup:** consider putting `NPM_TOKEN` in a GitHub environment with required reviewers, so a tag push alone can't publish.
