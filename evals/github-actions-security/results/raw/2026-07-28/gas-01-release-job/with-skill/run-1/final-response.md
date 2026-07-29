Both files are updated and untracked changes are as expected. Summary of the work:

**`.github/workflows/ci.yml`**
- Added `tags: ['v*']` to the `push` trigger so tag pushes fire the workflow (needed for job-level `needs` to work — release depends on build within the same run, rather than the riskier `workflow_run` trigger).
- Added workflow-level `permissions: {}` and per-job least-privilege grants (`build`: `contents: read`; `release`: `contents: write`, needed only for `gh release create`).
- New `release` job: gated by `needs: build` and `if: startsWith(github.ref, 'refs/tags/v')`, so it only runs on tag pushes and only after `build` passes. It checks out the tag, builds, publishes to npm (`NODE_AUTH_TOKEN` from `secrets.NPM_TOKEN`), and creates a GitHub release via `gh release create` using the default `GITHUB_REF_NAME`/`GH_TOKEN` env vars (no `${{ }}` interpolation in `run:` blocks).
- Pinned `actions/checkout` and `actions/setup-node` to freshly resolved commit SHAs (v7.0.1, v7.0.0) with version comments, added `persist-credentials: false`, `timeout-minutes`, and a concurrency group per the security-hardening baseline.

**Verify loop**: `actionlint` clean; `zizmor --persona=pedantic` went from 5 findings (2 high: cache-poisoning via `setup-node`'s default caching; 1 help: undocumented write permission; 1 info) down to 1 remaining informational finding after fixing (disabled `package-manager-cache`, commented the `contents: write` grant). The one remaining finding — "prefer trusted publishing" — is the deliberate, documented exception the task required (publishing via `NPM_TOKEN` rather than OIDC), noted in a comment in the workflow.

**Not verified**: I didn't push a tag to actually execute this workflow on GitHub Actions (no remote push was requested/authorized), so this is structural verification only via `actionlint`/`zizmor`, not a live run.

**README.md** release section now documents: bump version → commit to main → tag (`git tag vX.Y.Z`) → push tag → CI takes over (build gate, npm publish, GitHub release).
