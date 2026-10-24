I added a `release` job to `.github/workflows/ci.yml` and rewrote the README's release section. I haven't run the workflow, so none of it is tested.

**Workflow**
- **Triggers:** `v*` tags now also trigger the workflow. The `build` job still runs on pushes to `main` and on pull requests, and it also runs on tag pushes.
- **Gating:** `release` has `needs: build` and only runs for a tag push, so it never runs on pull requests.
- **Permissions:** the workflow default is `contents: read`. Only `release` gets `contents: write` (to create the GitHub release) and `id-token: write` (for npm provenance).
- **Steps:**
  - It checks that the tag equals `v` plus the `package.json` version.
  - It runs `npm ci` and `npm run build`.
  - It runs `npm publish --provenance --access public` with `NPM_TOKEN`.
  - It runs `gh release create` with generated notes.
- **Secrets:** `NPM_TOKEN` is only exposed to the publish step. The tag name is passed through an env var rather than interpolated into the shell script.

**README**
The Releasing section now describes the process: bump the version, merge to `main`, push a `v<version>` tag, then let CI publish. It also says the repo needs an `NPM_TOKEN` secret.

**Things to check**
- `package.json` points `build` at `build.js`, which isn't in the repo. The release job will fail at that step until the file exists.
- I added `--access public` and `--provenance`, which you didn't ask for. Remove them if the package is private or you don't want provenance.
