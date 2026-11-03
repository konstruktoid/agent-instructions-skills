I added a `release` job to `.github/workflows/ci.yml` and rewrote the README's release section. I haven't run the workflow, because it needs a real tag push on GitHub, and I haven't committed anything.

**Workflow**
- **Trigger:** the push trigger now also fires on `v*` tags. The `build` job is unchanged and still runs on pushes to `main` and on pull requests.
- **Gating:** `release` has `needs: build` and only runs on a push of a `v*` tag, never on pull requests.
- **Steps:** it runs `npm ci` and `npm run build`. It then runs `npm publish` with `NPM_TOKEN`, and finally `gh release create` for the tag with generated notes.
- **Permissions:** the workflow default is `contents: read`. Only the `release` job gets `contents: write`, which it needs to create the release.
- **Secrets:** `NPM_TOKEN` is passed only to the publish step, as `NODE_AUTH_TOKEN`. The tag name goes into the release step through an env var rather than being interpolated into the shell command.

**README**
The new section describes the process: bump the version, tag and push, then CI builds, publishes and creates the release. It also lists the `NPM_TOKEN` secret requirement.

**Caveats**
- `npm publish` publishes whatever version is in `package.json`, not the tag name. I didn't add a check that the two match, so a mismatched tag would publish the wrong version. I noted this in the README. I can add a check step if you want one.
- `package.json` has a `build` script that runs `node build.js`, but there's no `build.js` in the repo. The release job will fail at the build step until that file exists.
