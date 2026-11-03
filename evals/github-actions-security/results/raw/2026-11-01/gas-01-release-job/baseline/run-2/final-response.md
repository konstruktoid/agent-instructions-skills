I added the release job to `.github/workflows/ci.yml` and rewrote the README's release section. I haven't run the workflow, and nothing is committed.

- **Triggers:** the workflow now also runs on pushes of tags matching `v*`. The `build` job still runs on pushes to `main` and on pull requests.
- **Release job:** it needs `build` to pass and only runs for `v*` tag pushes. It then does the following:
  1. Checks that the tag equals `v` plus the `package.json` version, and fails if not.
  2. Runs `npm ci` and `npm run build`.
  3. Publishes with `npm publish`, authenticating through `NODE_AUTH_TOKEN` set from `secrets.NPM_TOKEN`.
  4. Creates the GitHub release with `gh release create --generate-notes`.
- **Permissions:** the workflow defaults to `contents: read`. Only the release job gets `contents: write`, which it needs to create the release.
- **README:** the release section now describes the steps: bump the version, merge, push a `vX.Y.Z` tag, and the CI does the rest. It also notes the `NPM_TOKEN` requirement.

The `NPM_TOKEN` repository secret has to exist for the publish step to work. Also, `package.json` has a `build` script that runs `node build.js`, but there is no `build.js` in the repo. The release job will fail at the build step until that file exists.
