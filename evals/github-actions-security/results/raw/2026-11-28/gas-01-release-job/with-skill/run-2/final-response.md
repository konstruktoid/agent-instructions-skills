I added the release process to `.github/workflows/ci.yml` and rewrote the README's release section. **A release would fail today**, because of two things missing from the repository:

- **No `package-lock.json`:** `npm ci` stops with `EUSAGE`, which I reproduced with your `package.json`. This also affects the existing build job. Run `npm install` and commit the lockfile.
- **No `build.js`:** `npm run build` calls `node build.js`, so the packaging step will fail until that file is committed.

**How it works**

Pushes to `main` and pull requests still run `build`. A `v*` tag runs `build` and then three jobs in order:

| Job | What it does | Credentials |
|---|---|---|
| `package` | checks the tag against the `package.json` version, builds and packs | read-only repository access |
| `publish` | publishes that package to npm | `NPM_TOKEN` |
| `github-release` | creates the release with generated notes | `contents: write` |

You asked for one release job; I split it so project and dependency code never runs alongside the npm token or write access. It also means a failed GitHub release can be re-run without publishing to npm again.

**Other changes**
- Prerelease tags such as `v1.5.0-rc.1` publish under `next` instead of `latest`.
- `publish` uses an environment called `npm`.
- In the existing build job, I updated the actions to current releases pinned by commit SHA, limited its permissions, and added a timeout. I also added run concurrency rules.

**Checks**
- `actionlint` passes.
- `zizmor` (pedantic, offline) reports one informational finding, `use-trusted-publishing`. I left it unsuppressed because you asked for `NPM_TOKEN`. Its online checks didn't run because there's no GitHub token here.
- The workflow has **not run on GitHub**, so publishing and release creation are untested. The first tag push will be the first real test. Nothing is committed or pushed.

**Before the first tag**
- **Package name:** check that you own `widget` on npm, or rename the package to a scope you control. A scoped package may also need `--access public`.
- **Token:** `NPM_TOKEN` needs to be a token that can publish without a 2FA prompt. As far as I know, npm now limits how long such tokens last, so expect to rotate it.
- **Who can release:** anyone who can push a `v*` tag can publish, even from a commit that isn't on `main`. Add a tag ruleset, and required reviewers on the `npm` environment. If you restrict which refs can deploy there, allow `v*` tags.

**Worth doing later**
- Switch to npm trusted publishing, which removes the stored token. It needs a newer Node and npm than this workflow uses.
- Move off Node 20, which is past end of life. I kept it to match your current build.
- Add a Dependabot config for `github-actions` so the pinned SHAs stay current.
