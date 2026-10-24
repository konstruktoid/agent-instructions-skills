I added the release job to `.github/workflows/ci.yml` and rewrote the README's release section. `actionlint` and `zizmor` (pedantic) both come back clean. I haven't run the workflow, because that needs a push and a real tag. zizmor reports "1 suppressed", but I added no `zizmor.yml` or other suppression.

**Release job**
- **Trigger:** the workflow now also fires on `v*` tag pushes, and the job runs only for a tag. It has `needs: build`, so it waits for the build job to pass.
- **Version check:** it fails if the tag doesn't equal `v` plus the `package.json` version.
- **Publish:** it runs `npm ci` and `npm run build`, then `npm publish --provenance` with `NPM_TOKEN`. The token is set only on the publish step.
- **GitHub release:** it runs `gh release create` with generated notes, using the built-in token, so no third-party action is involved.
- **Build job:** it still runs on pushes to main and on pull requests. It also runs on tag pushes now, since the release job depends on it.

**Security hardening I also applied**
- Workflow-level `permissions: {}`. The build job gets `contents: read`. The release job gets `contents: write` for the release and `id-token: write` for the npm provenance attestation, each with a comment.
- `actions/checkout` is pinned to v7.0.1 and `actions/setup-node` to v7.1.0, both resolved from the repos just now. Both previously used `@v4`. Release notes and breaking changes for the jump from v4 to v7 were not reviewed (only setup-node v7.1.0's notes were read), and setup-node v7.1.0 is a major bump you should check in the PR.
- `persist-credentials: false` on checkout, `timeout-minutes: 10` on both jobs, and job names.
- Dependency caching is off in both jobs, so a poisoned cache can't reach a published release.
- A concurrency group that cancels superseded runs but never cancels a tag run.

**README:** it now describes the bump, tag and push steps, what the job does, and the `NPM_TOKEN` requirement. It also says that if a release fails after the npm publish, you create the GitHub release by hand, because npm versions can't be republished.

**Before the first release**
- Add the `NPM_TOKEN` repository secret.
- Consider moving it to a GitHub environment with required reviewers.
- Consider npm trusted publishing, which would remove the stored token.
- There is no `dependabot.yml` in the repo. I didn't add one, but it would keep the SHA pins current.
