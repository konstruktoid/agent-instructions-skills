I added a `release` job to `.github/workflows/ci.yml` and rewrote the README's release section. I haven't run the workflow, so none of it is tested. Nothing is committed.

**Workflow**
- **Triggers:** the workflow now also runs on pushes of `v*` tags. The `build` job still runs on pushes to `main` and on pull requests.
- **Gating:** `release` has `needs: build`. It only runs for tag pushes, so it never runs on pull requests or `main` pushes.
- **Release steps:**
  1. Check that the tag equals `v` plus the `package.json` version, and fail if they differ.
  2. Run `npm run build`.
  3. Run `npm publish --provenance --access public`, authenticated with `NPM_TOKEN`.
  4. Run `gh release create` for the tag with generated notes.
- **Permissions:** the workflow default is now `contents: read`. Only `release` gets `contents: write` (to create the release) and `id-token: write` (for npm provenance).
- **Secrets:** `NPM_TOKEN` is passed only to the publish step. The tag name goes through an env var rather than inline `${{ }}` in the scripts. Checkout uses `persist-credentials: false`.

**README**
- The release section now lists the steps: bump the version, merge to `main`, push a matching `vX.Y.Z` tag, and let CI publish.
- It also says `NPM_TOKEN` must be an npm automation token and what to do if the job fails.

**Things to check**
- `--access public` and `--provenance` assume `widget` is a public package on a public repo. Remove them if it's private.
- The build job doesn't run `npm run build`. Only the release job does, so a broken build won't show up until a tag is pushed.
- Actions are pinned to major tags (`@v4`), matching the existing file, rather than commit SHAs.
