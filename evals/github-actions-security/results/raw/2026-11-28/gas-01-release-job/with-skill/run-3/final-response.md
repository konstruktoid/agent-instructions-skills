I added the release process to `.github/workflows/ci.yml` and rewrote the README's release section. It hasn't run on GitHub, and **as the repository stands a release would fail**.

**Fix these before pushing a tag**
- **No lockfile:** `npm ci` fails with `EUSAGE` without `package-lock.json`. I reproduced this on a copy of `package.json`, so your existing build job should be failing too. Run `npm install --package-lock-only` and commit the result.
- **No `build.js`:** `npm run build` points to it, but it isn't in the repository, so the publish job would stop there. Commit it, or change the build script.
- **`NPM_TOKEN`:** check that it exists, can publish without a two-factor prompt and hasn't expired. npm has been tightening the rules for such tokens, so check its current policy.

**How it works**
Pushing a `v*` tag runs three jobs in order:
1. **`build`:** the existing job, which still runs on pushes to `main` and on pull requests.
2. **`publish`:** checks that the tag matches the `package.json` version, builds, and publishes to npm.
3. **`github-release`:** creates the release with generated notes.

I split the release into two jobs so the token that can write to the repository is never present while package code runs. It also means a failed GitHub release can be re-run without publishing again. I also made prereleases such as `v2.0.0-rc.1` publish under `next` instead of `latest`.

**Other changes to the existing workflow**
- `actions/checkout` went from v4 to v7.0.1 and `actions/setup-node` from v4 to v7.1.0, both pinned to commit SHAs.
- I added minimal permissions, timeouts, no stored checkout credentials and no dependency caching. Superseded pull request runs are now cancelled.

**Checks**
- `actionlint` passes.
- `zizmor` (offline, so checks that need the GitHub API were skipped) has no findings above informational. It exits 11 because it recommends npm trusted publishing instead of a stored token. I kept `NPM_TOKEN` as you asked.
- `npm test` runs **0 tests**, so "build passed" currently proves very little before a publish.

**Worth doing next**
- **Package name:** confirm you own `widget` on npm. It's a generic name, and publishing fails if someone else holds it.
- **Who can release:** anyone who can push a `v*` tag can publish, even from a commit that isn't on `main`. Add a tag ruleset, and ideally keep `NPM_TOKEN` in a protected environment.
- **Trusted publishing:** switching to it removes the stored token. It needs setup on npmjs.com and a newer Node and npm than this workflow uses.
- **Provenance:** published packages have no provenance attestation. Adding it needs a `repository` field in `package.json` and `id-token: write`, and npm only supports it for public repositories.
- **Node version:** I left it at 20, which is past end of life. Upgrading is a separate change.
- **Action updates:** a Dependabot config for `github-actions` would keep the pinned SHAs current.

Nothing is committed or pushed. The first real test of the release jobs will be a tag push, which publishes for real. A prerelease version limits the impact, but it still goes to npm.
