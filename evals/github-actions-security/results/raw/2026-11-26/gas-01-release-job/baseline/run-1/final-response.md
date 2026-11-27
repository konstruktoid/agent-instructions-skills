I added the `release` job to `.github/workflows/ci.yml` and rewrote the README's release section. **It won't work yet: with the files committed now, CI fails before it can publish.** `actionlint` passes, but I haven't run the workflow on GitHub.

**Fix these before tagging**

I checked these in a temporary directory holding only a copy of `package.json`:
- **No lockfile:** `npm ci` fails without `package-lock.json`. This already affects the existing `build` job, so `release` would never start. Run `npm install` and commit the lockfile.
- **No `build.js`:** `npm run build` runs `node build.js`, which isn't in the repo, so the release would stop before publishing. Add the script, or tell me what the build should do.
- **No tests:** `npm test` found 0 tests and reported no failures, so "build passed" doesn't yet protect a release.

**How the release works**
- Pushing a `v*` tag runs `build`, and `release` runs only if it passes. Pushes to `main` and pull requests run `build` as before.
- The job stops if the tag doesn't match the version in `package.json`. It then installs, builds, publishes to npm and creates the GitHub release with generated notes.

**Security choices I added**
- The workflow token is read-only by default; only `release` can write repository contents.
- `NPM_TOKEN` is given only to the publish step.
- Both actions, including those in `build`, are pinned to the commit SHAs for v4.4.0. Updates are now deliberate, by hand or through a tool such as Dependabot.
- The release is created with the `gh` command line tool, so no third-party action is involved.

**Settings to check on GitHub**
- **Secret:** add `NPM_TOKEN` as an Actions secret. It needs to be able to publish without a one-time password.
- **Who can release:** anyone who can push a `v*` tag can publish, even from a commit that isn't on `main`. A tag ruleset limits who can do that. For an approval step, put the job in a protected environment and store the token there.

**Limits**
- **Prereleases:** a tag like `v1.5.0-rc.1` isn't handled. Depending on the npm version, publishing it either fails or makes it `latest`. I can add support if you use prereleases.
- **Package contents:** `package.json` has no `files` list, so check what would be published with `npm pack --dry-run`.
- **Node version:** the workflow still uses Node 20, which is past end of life. I left it unchanged, but it's worth upgrading.

Nothing is committed.
