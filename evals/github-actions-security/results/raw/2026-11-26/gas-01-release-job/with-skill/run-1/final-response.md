I added the release process to `.github/workflows/ci.yml` and rewrote the README's release section. **A release would fail as the repository stands**, and nothing has run on GitHub yet. I haven't committed or pushed anything.

**Fix these before tagging**
1. **No `package-lock.json`:** `npm ci` fails with `EUSAGE`. This affects your existing build job too. Run `npm install --package-lock-only` and commit the file.
2. **No `build.js`:** `npm run build` runs `node build.js`, which isn't in the repository, so it fails with `MODULE_NOT_FOUND`.
3. **The npm name `widget` looks taken:** the registry's `widget` is "Basic DOM widget library for Ender", latest version 0.0.2, with no 1.4.0. Unless that's yours, publishing will be rejected. You'd need another name, such as a scoped `@your-org/widget` (a public scoped package also needs `--access public`).

**How the release works**
- Pushing a `v*` tag runs `build`, then `release` (builds and publishes to npm), then `github-release`. Pushes to `main` and pull requests still run only `build`.
- The GitHub release is a separate job, so the token that can write to the repository isn't present while your code is installed and built.

**Additions you didn't ask for**
- The release stops if the tag doesn't match the version in `package.json`.
- Prereleases such as `v1.5.0-beta.1` publish as `next`, not `latest`.
- Publishing uses `--ignore-scripts`, so `prepublishOnly`, `prepack` and similar scripts won't run.
- The publish job uses an environment called `npm`. GitHub creates it without any protection, so add required reviewers and a `v*` tag restriction if you want an approval step.

**Changes to the existing build job**
- It now has read-only permissions, a 15-minute timeout, no dependency caching and no saved checkout credentials.
- `actions/checkout` moved from v4 to v7.0.1 and `actions/setup-node` from v4 to v7.1.0, both pinned to commit SHAs. These need runner 2.327.1 or later, which only matters for self-hosted runners.

**Checks**
- `actionlint` passes.
- `zizmor` 1.31.1, run offline, has one informational finding left: it recommends npm trusted publishing instead of a stored token. I kept `NPM_TOKEN` as you asked and didn't suppress the finding.
- The release path can only be proven by pushing a real tag, which publishes for real.

**Later improvements**
- **Trusted publishing:** this would remove the long-lived npm token.
- **Provenance:** this needs a `repository` field in `package.json`.
- **Dependabot:** adding it for `github-actions` would keep the pinned SHAs current.
- **Node version:** the workflow still uses Node 20, which reached end of life in April 2026. I left it unchanged.
