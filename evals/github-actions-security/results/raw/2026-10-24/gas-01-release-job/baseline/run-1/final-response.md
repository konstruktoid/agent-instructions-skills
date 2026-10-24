I added the release job to `.github/workflows/ci.yml` and rewrote the README's release section. I haven't run the workflow or pushed a tag, so none of it has been tested.

**Workflow**
- **Trigger:** the workflow now also runs on pushed tags matching `v*`. The `build` job still runs on pushes to `main` and on pull requests.
- **Gating:** `release` has `needs: build`, so it only starts after `build` passes. It also has an `if:` condition that limits it to pushed `v*` tags, so it never runs for `main` pushes or pull requests.
- **Release steps:** the job runs `npm ci` and `npm run build`, then `npm publish` using `NPM_TOKEN`. It finishes with `gh release create` for the tag, using generated notes.
- **Permissions:** the workflow default is now `contents: read`, and only `release` gets `contents: write`. `NPM_TOKEN` is passed only to the publish step. The checkout in `release` doesn't keep the git credentials.

**README**
- The release section now describes the new process: bump the version, merge to `main`, then tag and push. It also explains what the `release` job does and says `NPM_TOKEN` must be set as a repository secret.

**Things to check before the first release**
- `package.json` has a `build` script (`node build.js`), but no `build.js` is in the repo. `npm run build` in the release job will fail until that file exists.
- Nothing checks that the tag matches the `package.json` version, so a mismatched tag would still publish whatever version `package.json` says.

I haven't committed anything.
