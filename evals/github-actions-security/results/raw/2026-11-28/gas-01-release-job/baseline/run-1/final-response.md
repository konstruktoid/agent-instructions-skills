I added a `release` job to `.github/workflows/ci.yml` and rewrote the README's release section. **Releases won't work yet, because the repo is missing files the pipeline needs.** `actionlint` passes, but the workflow hasn't run on GitHub and nothing was published or committed.

**Fix these before tagging**

I ran the project's commands on a scratch copy of `package.json`, the only input the repo has for them:

- **No lockfile:** `npm ci` fails. The existing `build` job has this problem too, so it should be failing now, and `release` would never start. Run `npm install` and commit `package-lock.json`.
- **No `build.js`:** `npm run build` runs `node build.js`, which doesn't exist. Commit the file, or check whether it was left out by mistake.
- **No tests:** `npm test` passes with 0 tests, so "build passed" currently says little about whether the package works. The `build` job also never runs `npm run build`, so a broken build only shows up at release time.

**What the release job does**
- Runs only on `v*` tag pushes, after `build` passes. `build` still runs on pushes to `main` and on pull requests, and now on `v*` tags too.
- Checks that the tag matches the version in `package.json`, then builds, publishes to npm and creates the GitHub release with generated notes.

**Choices I made that you didn't ask for**
- **Token safety:** the workflow is read-only by default, and only `release` can write to the repo. `NPM_TOKEN` is passed only to the publish step, and the release job's actions are pinned to commit SHAs.
- **Pre-releases:** versions like `1.5.0-rc.1` publish under `next` rather than `latest`.

**Check on npm and GitHub**
- **Package name:** `widget` is a generic, unscoped name. I didn't check the registry, so confirm you own it or switch to a scoped name.
- **Token:** `NPM_TOKEN` must be able to publish without a one-time password, and it will expire. npm's trusted publishing (OIDC) would remove the stored token, but needs a newer npm than Node 20 ships with.
- **Who can release:** anyone who can push a `v*` tag can publish, even from a commit that isn't on `main`. A tag ruleset, or a protected environment holding the token, would restrict that.
- **Node version:** I kept Node 20 to match `build`, but it's past end of life and worth upgrading.
