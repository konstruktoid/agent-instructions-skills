I added a `release` job to `.github/workflows/ci.yml` and rewrote the README's release section. I haven't run the workflow or committed anything.

**Workflow**
- **Triggers:** the workflow now also runs on `v*` tag pushes. The `build` job is unchanged and still runs on pushes to main and on pull requests. On a tag push it runs first as well.
- **Release job:** it has `needs: build` and an `if` condition, so it only runs on a `v*` tag and only after `build` passes. It runs `npm ci` and `npm run build`, then `npm publish`.
- **GitHub release:** the job creates the release with `gh release create`, using the tag name and generated release notes.
- **Permissions:** the workflow defaults to `contents: read`, and only the release job gets `contents: write`.
- **Secrets:** `NPM_TOKEN` is passed only to the publish step, as `NODE_AUTH_TOKEN`.

**README**
The release section now describes the steps. Bump the version in `package.json`, merge to main, push a tag such as `v1.5.0`, and the workflow does the rest. It also notes the `NPM_TOKEN` secret requirement.

**Things to check**
- `package.json` has a `build` script (`node build.js`), but there is no `build.js` in the repo. `npm run build` will fail in the release job until that file exists.
- Nothing checks that the tag matches the `version` in `package.json`. If they differ, npm publishes the `package.json` version.
- I didn't add npm provenance. That would need `id-token: write` permission and `--provenance` on the publish command.
