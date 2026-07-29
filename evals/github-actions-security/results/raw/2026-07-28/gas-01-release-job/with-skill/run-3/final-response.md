Both hardening tools are clean except one deliberate, documented exception. Summary:

**Verify loop (2 attempts):**
- `actionlint`: clean (exit 0)
- `zizmor --persona=pedantic`: went from 6 findings (2 high, 2 low, 1 help, 1 info) to 1 informational finding — `use-trusted-publishing`, which is expected since you asked for `NPM_TOKEN`-based publishing rather than OIDC trusted publishing. It's documented with a comment on the `npm publish` step.
- No live run: this sandbox repo has no `git remote`, so I couldn't push a tag and watch the workflow execute on GitHub. Verification is structural (lint + security audit) only — flagging that per the checklist rather than claiming an end-to-end pass.

**What changed** (`.github/workflows/ci.yml`):
- `permissions: {}` at workflow level, `contents: read`/`contents: write` scoped per job, workflow-level `concurrency` group added
- `actions/checkout` and `actions/setup-node` pinned to their latest release SHAs (`v7.0.1`, `v7.0.0`) with `persist-credentials: false` and caching disabled (cache-poisoning risk on a job that publishes)
- Existing `build` job now also triggers on `v*` tag pushes (still runs on `main` pushes and PRs) — this is what lets `release` gate on it
- New `release` job: `needs: build`, `if: startsWith(github.ref, 'refs/tags/v')`, checks out, builds, runs `npm publish` with `NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}`, then `gh release create` using the tag name via `env:` (not interpolated into the shell) with `contents: write` and a comment explaining the scope
- Every job has `timeout-minutes: 10`

README's "Releasing" section now describes tagging `v*` and pushing it to trigger the automated release, instead of the old manual/by-hand process.
