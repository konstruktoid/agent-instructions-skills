I added the release job to `.github/workflows/ci.yml` and rewrote the README's release section. I haven't run the workflow. It needs a real `v*` tag push and an `NPM_TOKEN` secret, and I didn't push anything.

`actionlint` is clean. `zizmor` (pedantic) reports one informational finding, which is expected: it prefers npm trusted publishing over a stored token, but you asked for `NPM_TOKEN`. One other finding is suppressed in zizmor's output and I didn't look into it. I did not add any suppressions of my own.

**Workflow**
- **Triggers:** `v*` tags are added to the push trigger. The `build` job still runs on pushes to `main` and on pull requests, and it also runs on tag pushes, because `release` waits for it.
- **Release job:** it runs only on tag pushes and only after `build` passes. It rebuilds the package and checks that the tag matches the `package.json` version, so `v1.5.0` fails if the version is still `1.4.0`. It then runs `npm publish` and creates the GitHub release with `gh release create --verify-tag --generate-notes`.
- **Secrets and permissions:** `NPM_TOKEN` is passed only to the publish step. Permissions are `{}` at the workflow level, `contents: read` for `build`, and `contents: write` for `release`.
- **Hardening I added:** `timeout-minutes`, `persist-credentials: false`, and a `concurrency` group that cancels only pull request runs. I also turned off setup-node's package-manager cache so nothing cached is restored into the job that publishes.

**Action versions:** I pinned both actions to commit SHAs for the latest releases: `actions/checkout` v7.0.1 and `actions/setup-node` v7.0.0. Both are major-version bumps from the `@v4` the file used, and I did not read their release notes. The first real run will show whether the bump changes anything.

**README:** the release section now describes the steps: bump the version and merge to `main`, tag it `vX.Y.Z` and push the tag, and let `build` then `release` run. It also notes that `NPM_TOKEN` must be an npm automation token and that a failed publish needs a new tag.

**Optional follow-up:** moving to npm trusted publishing (OIDC) would remove the stored token. I didn't do it because you specified `NPM_TOKEN`.
