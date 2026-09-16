`actionlint` is clean. `zizmor` reports 2 low-severity `concurrency-limits` findings in `ci.yml` and `dependency-review.yml` — these are pre-existing (missing workflow-level `concurrency:` block), not introduced by this change, and out of scope for this fix.

**Root cause:** not the harden-runner pin. The failed log's `Post Harden Runner` block shows `domain not allowed: api.deps.dev.` — `dependency-review-action` calls deps.dev to enrich results when the PR actually changes a dependency manifest, and that endpoint was never in `allowed-endpoints`. The "last passing" run you saved is from a PR that didn't touch a manifest, so it never exercised that code path — it's not evidence the old harden-runner version worked and the new one doesn't. Rolling back the pin would leave `api.deps.dev` blocked and fail again on the next PR that touches a dependency file, regardless of harden-runner version.

**Fix applied:** added `api.deps.dev:443` to `allowed-endpoints` in `.github/workflows/dependency-review.yml`. Left the harden-runner pin at v2.21.0.

**Unverified:** this is a behavioral fix to an egress allowlist — `actionlint`/`zizmor` can't exercise it. It's only confirmed once the workflow actually runs on a PR that changes a dependency manifest. I haven't pushed or dispatched anything; let me know if you want this committed and pushed so the check re-runs on your PR.

File changed: `.github/workflows/dependency-review.yml`.
