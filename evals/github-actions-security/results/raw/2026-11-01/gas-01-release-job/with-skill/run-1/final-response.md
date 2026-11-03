I added the release job and rewrote the README's release section. I couldn't run the workflow itself, so the publish path is untested. I didn't push a branch or tag, because that would trigger a real npm publish and release.

**Workflow (`.github/workflows/ci.yml`)**
- **Triggers:** `build` still runs on pushes to `main` and on pull requests. I also added `v*` tag pushes as a trigger, because `release` can only follow a passing `build` run for the same tag.
- **`release` job:** it has `needs: build` and only runs for `v*` tags. It runs `npm ci` and `npm run build`, then checks that the tag equals `v` plus the `package.json` version. It then runs `npm publish` with `NPM_TOKEN`, and creates the GitHub release with `gh release create --generate-notes`.
- **Permissions:** the workflow starts with none. `build` gets `contents: read`. `release` gets `contents: write`, and only `release` has the npm token.
- **Hardening:** I SHA-pinned the actions to their latest releases: `actions/checkout` v7.0.1 and `actions/setup-node` v7.1.0. I also set `persist-credentials: false`, job timeouts, and a concurrency group that never cancels a run.
- **Cache:** I turned off setup-node's cache, so a publishing job never restores one. I used `gh` for the release rather than a third-party release action, so there is one less dependency in a job that holds a write token.

**README:** the "Releasing" section now lists the steps: bump the version, merge, tag `vX.Y.Z`, push the tag. It also explains what the jobs do, and notes that a failed npm publish needs a new version, since npm versions can't be republished.

**Checks**
- `actionlint` is clean.
- `zizmor` (pedantic) has one informational finding left: it suggests npm trusted publishing (OIDC) instead of a stored token. I left that alone because you asked for `NPM_TOKEN`. Switching would remove the long-lived secret.

**For you to do**
- Add `NPM_TOKEN` as a repository secret.
- Consider putting the release job behind a GitHub Environment with required reviewers and a tag rule.
- Consider adding a Dependabot config with a cooldown for the action pins. I didn't add one because it's outside this request.
