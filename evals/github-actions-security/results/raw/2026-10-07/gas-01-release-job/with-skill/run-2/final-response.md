I added the release job to `.github/workflows/ci.yml` and rewrote the README's release section. `actionlint` is clean. `zizmor` (pedantic) has one remaining finding, which I left on purpose (explained below). I did not push anything or trigger a run, so the job has never run on a real tag.

**Workflow**
- The workflow now also triggers on pushes of tags matching `v*`. `build` still runs on pushes to `main` and on pull requests.
- `release` has `needs: build` and only runs for `v*` tags. Its steps are:
  1. Check that the tag equals `v` plus the `package.json` version, and fail if they differ.
  2. Run `npm ci` and `npm run build`.
  3. Run `npm publish` with `NPM_TOKEN`, which is passed only to that step.
  4. Run `gh release create` for the tag with generated notes. I used the `gh` CLI instead of a third-party action.
- I also tightened the existing workflow:
  - Permissions are `{}` at workflow level, with `contents: read` on `build` and `contents: write` on `release` (commented).
  - Both jobs have timeouts, and checkout uses `persist-credentials: false`.
  - There is a concurrency group that never cancels a tag run.
  - Both jobs have names.
- The actions are pinned to commit SHAs that I looked up during this change:
  - `actions/checkout` is v7.0.1.
  - `actions/setup-node` is v7.0.0.

  Both are the latest releases and were published more than a week ago. This is a major bump from `@v4` for both. I read the `setup-node` v7 release notes but not the checkout ones.
- I set `package-manager-cache: false` on `setup-node` in both jobs. Without it, `zizmor` flagged cache poisoning risk on a publishing workflow.

**README**
The release section now describes the steps: bump the version and merge, push a `vX.Y.Z` tag, then the workflow builds, publishes and creates the release. It also states that the tag must match `package.json` and that `NPM_TOKEN` must be an npm automation token.

**The remaining `zizmor` finding**
It suggests npm trusted publishing (OIDC) instead of a stored token. I kept `NPM_TOKEN` because you asked for it. Trusted publishing would remove the long-lived secret. It would need `id-token: write` and a trusted-publisher setting on npm.

**Setup you still need to do**
Add the `NPM_TOKEN` repository secret. Consider storing it as an environment secret on a protected environment, so publishing needs reviewer approval.
