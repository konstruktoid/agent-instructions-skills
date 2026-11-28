I added the release process to `.github/workflows/ci.yml` and rewrote the README's release section. **Neither the build nor a release will work yet, because two files are missing from the repository:**

- **`package-lock.json`:** `npm ci` fails without it, so the existing build job fails too. Running `npm install` and committing the lockfile fixes this.
- **`build.js`:** `npm run build` points to it, so the publish job would fail at that step. Add the script, or tell me what "build" should do.

I reproduced both failures locally in a copy containing only `package.json`. I didn't make up either file.

**How a release works now**
- Pushes to `main` and pull requests run `build` as before. Pushing a `v*` tag runs it too.
- `publish` runs only for tags, after `build` passes. It checks that the tag matches the version in `package.json`, builds, and publishes with `NPM_TOKEN`.
- `github-release` runs after `publish` succeeds and creates the release with generated notes.

I split the release into two jobs so the token that can write to the repository is never present while package code runs.

**Other changes you didn't ask for**
- Each job now has only the permissions it needs, plus a timeout.
- Actions are pinned to commit SHAs and upgraded from v4: `checkout` to v7.0.1 and `setup-node` to v7.1.0.
- Package caching is off, and `npm publish` uses `--ignore-scripts`. If you later rely on `prepack` or `prepublishOnly`, those won't run.
- A newer pull request run now cancels the older one. Release runs are never cancelled this way.

**Checks**
- `actionlint` is clean.
- `zizmor` (offline, so checks that need the GitHub API were skipped) is not fully clean. It suggests npm trusted publishing instead of a stored token. Its strictest mode also warns that `NPM_TOKEN` isn't protected by a GitHub environment. I suppressed neither.
- The workflow hasn't run on GitHub. The first real test is a pull request for `build`, then a tag push for the release, which really publishes.

**Before your first tag**
- Add the `NPM_TOKEN` secret.
- Restrict who can create `v*` tags with a tag ruleset. Anyone who can push one can publish, even from a commit that isn't on `main`.

**Worth doing later**
- **Trusted publishing:** this lets npm accept the workflow's identity, so you can drop the stored token.
- **Environment:** until then, moving `NPM_TOKEN` into an environment with required reviewers adds an approval step before publishing.
- **Node version:** the workflow still uses Node 20, which is past end of life. I left the upgrade to you.
- **Action updates:** a Dependabot config for `github-actions` would keep the pinned SHAs current.
- **Prereleases:** a tag like `v1.5.0-rc.1` isn't handled and shouldn't be pushed; the README says so.

Nothing is committed or pushed.
