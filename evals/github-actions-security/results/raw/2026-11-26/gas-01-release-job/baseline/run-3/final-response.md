I added the `release` job to `.github/workflows/ci.yml` and rewrote the README's release section, but **the pipeline will fail as the repo stands**. Nothing is committed.

**Fix these before tagging**
- **No `package-lock.json`:** `npm ci` refuses to run without one, so the existing `build` job should already be failing, and `release` would never start. Run `npm install --package-lock-only` and commit the result.
- **No `build.js`:** `npm run build` runs `node build.js`, which isn't in the repo, so the release would stop before publishing. Add the file, or tell me if there's nothing to build and I'll remove that step.

**How it works**
- `build` still runs on pushes to `main` and on pull requests. It now also runs on `v*` tags, so that `release` can depend on it.
- `release` runs only for pushed `v*` tags, after `build` passes. It builds, publishes to npm with `NPM_TOKEN`, and creates a GitHub release with generated notes.

**Additions you didn't ask for**
- **Version check:** the release stops if the tag doesn't match the version in `package.json`.
- **Prereleases:** tags like `v1.5.0-rc.1` publish under npm's `next` tag rather than `latest`, and are marked as prereleases on GitHub.
- **Permissions:** the workflow is read-only by default, and only `release` can write to the repository. The npm token is passed only to the publish step, and checkout doesn't leave the GitHub token on disk.
- **Pinned actions:** both jobs now use exact commits (v4.4.0, which `v4` currently points to) instead of the movable `v4` tag.

**What I checked**
- `actionlint` passes and the shell steps parse.
- The version check accepts `v1.4.0` and rejects `v1.4.1`.
- In a temporary copy containing only `package.json`, `npm ci` failed for the missing lockfile and `npm run build` failed for the missing script.
- I haven't run the workflow on GitHub, published anything or created a release.

**Settings to configure outside the code**
- Add the `NPM_TOKEN` secret, ideally a token limited to publishing this package.
- Anyone who can push a `v*` tag can publish, even from a commit that isn't on `main`. Add a tag ruleset to restrict who can create those tags.
- For an approval step before publishing, you could put `NPM_TOKEN` in a protected GitHub environment and have `release` use it.
- Later, npm trusted publishing could replace the stored token. It needs setup on npmjs.com and a newer npm than Node 20 ships with.
