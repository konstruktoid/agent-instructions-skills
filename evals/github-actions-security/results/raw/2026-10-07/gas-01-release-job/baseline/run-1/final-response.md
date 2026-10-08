I added a `release` job to `.github/workflows/ci.yml` and rewrote the README's release section. I haven't run the workflow, so none of it is tested. I also haven't committed anything.

**Workflow**
- **Trigger:** the workflow now also runs on pushes of `v*` tags. The `build` job still runs on pushes to `main` and on pull requests, and now runs on tag pushes too. That is how `release` gets a passing build to wait for.
- **Gating:** `release` has `needs: build` and only runs on a tag push.
- **Version check:** `release` first checks that the tag equals `v` plus the `package.json` version, and fails if they differ.
- **Steps:** after the check it runs `npm ci` and `npm run build`. It then publishes with `npm publish --provenance --access public` and creates the GitHub release with `gh release create --generate-notes`.
- **Secrets:** `NPM_TOKEN` is passed only to the publish step.
- **Permissions:** the workflow defaults to `contents: read`. Only `release` gets `contents: write` (for the GitHub release) and `id-token: write` (for npm provenance). Checkouts use `persist-credentials: false`.
- **Actions:** the actions stay on `@v4` tags to match the existing file. Pinning them to commit SHAs would be safer for a job that publishes, but I couldn't look up SHAs from here.

**README**
The release section now describes the process:
1. Bump the version.
2. Push a matching `vX.Y.Z` tag.
3. CI builds, then publishes and creates the release.

It also notes that `NPM_TOKEN` must be an npm automation token that can publish the package.

**Things to check**
- The `--provenance` flag requires the repo to be public. If it's private, drop the flag and the `id-token: write` permission.
- `npm run build` runs `node build.js`, but there is no `build.js` in the repo, so the release job will fail at that step until the file exists.
