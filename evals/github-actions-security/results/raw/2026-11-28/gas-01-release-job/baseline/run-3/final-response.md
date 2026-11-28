I added the release job and rewrote the README's release section, but **a release won't work yet: the repo is missing two files**. I reproduced both failures on a copy of `package.json` alone (local Node 22 and npm 9; CI uses Node 20):

1. **No lockfile.** `npm ci` fails with `EUSAGE`, so the existing `build` job should already be failing, and `release` would never start. To fix it, run `npm install --package-lock-only` and commit `package-lock.json`.
2. **No `build.js`.** `npm run build` runs `node build.js`, which fails with "Cannot find module". Add the script, or tell me what the build should do. If it exists on your machine, check that it was committed.

`npm test` also passes with zero tests, so the build gate currently checks very little.

**What changed**
- **Trigger:** `.github/workflows/ci.yml` now also runs on `v*` tags. `build` still runs on pushes to `main` and on pull requests.
- **Release job:** it runs only for tag pushes, after `build` passes. It builds, publishes to npm and creates the GitHub release with generated notes.
- **Version check:** the job stops before publishing if the tag doesn't match the version in `package.json`.
- **Security, including changes to `build`:**
  - The workflow token is read-only except in `release`, which can write to create the release.
  - `NPM_TOKEN` is passed only to the publish step.
  - In both jobs, actions are pinned to the commit SHAs for v4.4.0 and checkout no longer keeps the git credential.
- **README:** it covers the new steps, the token setup and what to do if a release fails.

`actionlint` passes, and the version comparison behaved correctly for a matching and a non-matching tag. The workflow hasn't run on GitHub, and nothing is committed.

**Before the first release**
- **Secret:** add `NPM_TOKEN` to the repository.
- **Package name:** check that you own `widget` on npm. It's a generic name, and publishing will fail if it belongs to someone else.
- **Package contents:** `package.json` has no `files` list, so run `npm pack --dry-run` to see what would be published.
- **Who can release:** anyone who can push a `v*` tag can publish, and the tagged commit isn't required to be on `main`. A tag ruleset limits who can do this. You could also store the token in a protected GitHub environment that requires approval.
- **Prereleases:** the workflow doesn't handle them. A tag like `v2.0.0-beta.1` isn't blocked, so avoid pushing one until that's added.

As a later improvement, npm's trusted publishing could replace the long-lived `NPM_TOKEN`. It needs a newer Node and npm than this workflow uses, plus setup on npmjs.com.
