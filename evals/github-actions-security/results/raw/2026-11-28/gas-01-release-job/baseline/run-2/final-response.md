I added the `release` job to `.github/workflows/ci.yml` and rewrote the README's release section. `actionlint` passes, but **the pipeline won't work yet**, and I haven't run it on GitHub.

**Fix these before pushing a tag**
1. **No lockfile:** `npm ci` fails without `package-lock.json`, which I confirmed on a copy of `package.json`. The existing `build` job has the same problem, so `release` would never start. Run `npm install` and commit the lockfile.
2. **No `build.js`:** `npm run build` runs `node build.js`, which isn't in the repo, so the release job would fail there. Add the file or correct the script.
3. **Package name:** the public npm registry already has a `widget` package (latest version 0.0.2). Unless your npm account has publish rights to it, publishing will be rejected, and you'd need another name, such as a scoped `@your-org/widget`. A scoped package that should be public also needs `npm publish --access public`.
4. **Secret:** add `NPM_TOKEN` in the repository's Actions secrets, if it isn't there already. It needs to be a token that can publish from CI without a one-time password prompt.

**How the release works**
- Pushing a `v*` tag runs `build`, and `release` starts only if it passes. Pushes to `main` and pull requests still run `build` as before.
- The release job checks the tag against `package.json`, installs, builds, publishes to npm, then creates the GitHub release with generated notes.

**Choices I made that you didn't ask for**
- **Tag check:** a tag like `v1.5.0` fails the release if `package.json` says anything else.
- **Prereleases:** hyphenated versions such as `v1.5.0-rc.1` go to the npm `next` tag instead of `latest`, and are marked as prereleases on GitHub.
- **Permissions:** the workflow is read-only by default, and only `release` can write repository contents. The npm token is given only to the publish step.
- **Pinned actions:** the release job pins `checkout` and `setup-node` to the v4.4.0 commits. `build` still uses `@v4`.
- **Failed releases:** the README explains what to do if npm publishing succeeds but creating the GitHub release fails.

**Optional hardening:** anyone who can push a `v*` tag can trigger a publish, even from a commit that isn't on `main`. To limit this, add a tag ruleset restricting who can create `v*` tags. You could also store `NPM_TOKEN` in a protected environment with required reviewers, which means adding `environment:` to the release job.

Nothing is committed; the changes are in your working tree.
