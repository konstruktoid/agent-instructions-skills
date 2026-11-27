The workflow and README are written. `actionlint` passes; local runs show problems already in the repo, which I'm including in the summary.

I added the release process to `.github/workflows/ci.yml` and rewrote the README's release section. **As the repo stands, a release would fail**, and so would the existing build job.

**Fix these before tagging**
- **No `package-lock.json`:** `npm ci` fails with `EUSAGE`, so the build job can't pass and nothing gets published. Running `npm install` and committing the lockfile fixes this.
- **No `build.js`:** `npm run build` runs `node build.js`, which isn't in the repo, so publishing would stop there. If it only exists on your machine, commit it.
- **No tests found:** `npm test` passes with 0 tests, so "build passed" currently checks very little.

**How the release works**
A `v*` tag runs `build`, then `publish`, then `github-release`. I used two release jobs so the npm token and the repository write permission are never in the same job. Pushes to `main` and pull requests still run only `build`.

**Changes beyond what you asked for**
- **Tag check:** publishing stops if the tag doesn't match the version in `package.json`.
- **Token safety:** only the publish step gets `NPM_TOKEN`, and it uses `--ignore-scripts`.
- **Hardening:**
  - Actions are pinned to commit SHAs and upgraded from v4 (`checkout` v7.0.1, `setup-node` v7.1.0).
  - Permissions are limited per job, jobs have timeouts, and dependency caching is off.
  - A newer pull request run now cancels the older one; publishing runs are never cancelled.

**Verification**
- `actionlint` is clean.
- `zizmor` 1.31.1, run offline, exits 11 with one informational finding: it recommends npm trusted publishing over a stored token. I left it unsuppressed because you asked for `NPM_TOKEN`.
- The workflow has **not run on GitHub**. Nothing was committed or pushed, so the first real test is a pull request for `build` and a tag push for the release.

**Worth deciding**
- **Pre-release tags:** a tag like `v1.5.0-beta.1` also triggers a release, and nothing marks it as a pre-release. The README says not to use them; I can add support if you need it.
- **Who can release:** anyone who can push a `v*` tag can publish. A tag ruleset, or an `npm` environment with required reviewers holding the token, would restrict that.
- **Trusted publishing:** switching to it would remove the long-lived token. It needs setup on npmjs.com and a newer npm than Node 20 ships with.
- **Node 20:** it's past end of life. I kept it to match your current CI.
- **Keeping pins current:** a Dependabot config for `github-actions` would update the pinned SHAs for you.
