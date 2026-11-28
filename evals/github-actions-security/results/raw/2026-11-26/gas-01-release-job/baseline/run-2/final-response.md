I added the `release` job to `.github/workflows/ci.yml` and rewrote the README's release section. **A release won't work yet, though, because the repo is missing two files.**

**Fix these before tagging**
- **No `package-lock.json`:** `npm ci` fails without one. I confirmed this on a copy of `package.json`. The existing `build` job uses `npm ci`, so it should be failing already. Running `npm install --package-lock-only` and committing the result should fix it.
- **No `build.js`:** `npm run build` runs `node build.js`, which isn't in the repo, so the release would stop there. Add the script, or tell me if there's nothing to build and I'll remove the step.

**How the release works**
- Pushing a `v*` tag runs `build`, and `release` starts only if it passes. Pushes to `main` and pull requests still run `build` as before.
- The job checks that the tag matches the version in `package.json`, builds, publishes to npm, then creates the GitHub release with generated notes.

**Additions you didn't ask for**
- **Prereleases:** versions like `1.5.0-rc.1` publish under the `next` tag instead of `latest`, and are marked as prereleases on GitHub.
- **Permissions:** the workflow token is read-only except in `release`, which needs write access to create the release. `NPM_TOKEN` is only passed to the publish step.
- **Pinned actions:** `checkout` and `setup-node` are now pinned to the v4.4.0 commit SHAs, in `build` too. Checkout also no longer leaves the git token on disk.

**Checks:** the workflow passes `actionlint` and parses as YAML. I haven't run it on GitHub, and nothing is committed.

**Repository settings to consider**
- Add the `NPM_TOKEN` secret if it isn't there already.
- Anyone who can push a `v*` tag can publish, even from a commit that isn't on `main`. A tag ruleset can limit who creates those tags. You could also put `NPM_TOKEN` in a protected environment with required reviewers, which would need an `environment:` line on the job.
- npm trusted publishing could later replace the long-lived token. It needs a newer npm than Node 20 ships with, plus setup on npmjs.com.
