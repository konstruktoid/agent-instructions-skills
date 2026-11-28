I added the release job to `.github/workflows/ci.yml` and rewrote the README's release section. **A release would fail as the repository stands**, and nothing has run on GitHub yet.

**Fix these before tagging**
1. **No lockfile:** `npm ci` fails with `EUSAGE` locally, so the existing CI build should be failing too. Run `npm install --package-lock-only` and commit `package-lock.json`.
2. **No `build.js`:** `npm run build` runs `node build.js`, which isn't in the repository, so every tag build would fail. Add the script, or tell me there's no build step and I'll remove it.
3. **Package name:** `widget` already exists on npm, and its latest version is `0.0.2`. Unless that package is yours, publishing will be rejected and you'll need another name, such as a scoped one. A scoped public package also needs `--access public` on the publish command.
4. **Secret:** add `NPM_TOKEN` as a repository secret.

`npm test` also runs zero tests, so "build passed" doesn't tell you much yet.

**How it works**
- Pushes to `main` and pull requests still install and test as before. A `v*` tag does the same, then builds, packs and uploads the tarball.
- The `release` job runs only for tags and only after `build` passes. It publishes that tarball to npm and creates the GitHub release with the tarball attached.
- Building happens in `build`, not `release`, so your npm token and write access are never present while install, test or build code runs.

**Additions you didn't ask for**
- The build fails if the tag doesn't match the version in `package.json`.
- Versions containing `-` (such as `1.5.0-rc.1`) go to npm's `next` tag and are marked as prereleases.
- I hardened the workflow: minimal permissions, actions pinned to commit SHAs, job timeouts, and no caching.
- `actions/checkout` went from v4 to v7.0.1 and `actions/setup-node` from v4 to v7.1.0. The new upload and download actions are at v7.0.2 and v8.0.2.

**Checks**
- `actionlint` passes.
- `zizmor` (pedantic, offline, so its online checks didn't run) exits 11 with one informational finding, `use-trusted-publishing`. I left it because you asked for `NPM_TOKEN`. Its summary also counts one suppressed finding; I added no suppressions.
- A dry-run pack and publish of a copy of `package.json` and the README worked. That doesn't test authentication or ownership of the name.
- The first real test is a pull request for `build`, then a tag push for `release`. A prerelease tag still publishes to npm for real.

**Worth doing later**
- **Trusted publishing:** npm can authenticate the workflow directly, so you wouldn't need a stored token. It needs a newer npm than Node 20 ships with.
- **Restrict who can release:** anyone who can push a `v*` tag can publish, even from a commit that isn't on `main`. A tag ruleset, or an `npm` environment with required reviewers holding the token, would close that.
- **Node version:** Node 20 is past end of life. I kept it so this change doesn't alter what you build against.
- **Keeping pins current:** a Dependabot config for `github-actions` would update the pinned SHAs.

Nothing is committed or pushed.
