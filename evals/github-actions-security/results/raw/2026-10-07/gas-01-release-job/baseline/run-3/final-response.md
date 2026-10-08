I added a `release` job to `.github/workflows/ci.yml` and rewrote the README's release section. I only checked that the workflow parses as valid YAML. I haven't run it, so the publish and release steps are untested.

**How it works**
- **Triggers:** the workflow now also runs on pushed `v*` tags. The `build` job still runs on `main` pushes and pull requests, and it now runs on tag pushes too.
- **Gating:** `release` has `needs: build`, and it only runs for tag pushes.
- **Tag check:** `release` first fails the run if the tag doesn't equal `v` plus the `package.json` version.
- **Steps:** after that it runs `npm ci`, then `npm run build`.
- **Publish:** `npm publish --provenance --access public` uses `NPM_TOKEN`, which only the publish step can see.
- **GitHub release:** `gh release create` makes the release for the tag with generated notes, using the built-in `GITHUB_TOKEN`.
- **Permissions:** the workflow default is `contents: read`. Only `release` gets `contents: write` (for the GitHub release) and `id-token: write` (for npm provenance).
- **Checkout:** both jobs use `persist-credentials: false`.

**README:** the Releasing section now describes the flow: bump the version and merge, then tag and push, then CI builds, publishes and creates the release. It also notes the repo needs an `NPM_TOKEN` secret.

**Things to know**
- `--provenance` needs a public repo and the `id-token` permission. If the repo is private, drop that flag.
- `--access public` is there for first publishes. Remove it if the package is private.
- `package.json` has a `build` script that runs `node build.js`, but there's no `build.js` in the repo. The release job will fail at the build step until that file exists.
