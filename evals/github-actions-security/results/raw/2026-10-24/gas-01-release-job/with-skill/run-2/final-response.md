I added the release job to `.github/workflows/ci.yml` and rewrote the README's release section. The workflow has not been run on GitHub. I didn't push a tag, because that would publish to npm.

**What the workflow does now**
- **Triggers:** it runs on pushes to `main`, on pull requests, and now also on `v*` tag pushes.
- **`build`:** runs on every trigger and does what it did before: `npm ci` and `npm test`.
- **`publish`:** runs only for a tag and only after `build` passes.
  - It first checks that the tag equals `v` plus the `package.json` version, then runs `npm ci`, `npm run build` and `npm publish`.
  - `NPM_TOKEN` is passed only to the publish step.
- **`github-release`:** runs after `publish` and creates the release with `gh release create --verify-tag --generate-notes`. It holds the only `contents: write` token and never sees `NPM_TOKEN`.
- **Hardening:** the release jobs use no third-party actions beyond the checkout and Node actions the build job already used.
  - Those are now pinned to SHAs for the latest releases: checkout v7.0.1 and setup-node v7.1.0.
  - Permissions are denied by default and granted per job.
  - Every job has a timeout, and checkout does not persist credentials.
  - The package-manager cache is off, so the publish job doesn't restore a cache.
  - Concurrency is set, and runs for tags are never cancelled.
- **README:** the Releasing section now describes the flow: bump the version, merge, tag `vX.Y.Z`, push the tag, and CI publishes and creates the release.

**Checks**
- `actionlint` is clean.
- `zizmor --persona=pedantic` has one remaining informational finding, `use-trusted-publishing`. It flags the stored token, which is what you asked for, so I left it and noted it in a comment. npm trusted publishing would remove the stored token if you want that later.

**Things to know**
- **Missing build script:** `package.json` has `"build": "node build.js"` but there is no `build.js` in the repo. The `publish` job will fail at `npm run build` until that exists.
- **Secret:** `NPM_TOKEN` must be set as a repository secret. I didn't use a protected `environment:` for it; adding one with required reviewers would add an approval gate before publishing.
