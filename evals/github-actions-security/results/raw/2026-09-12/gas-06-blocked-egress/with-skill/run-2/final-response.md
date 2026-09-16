`actionlint` is clean. `zizmor` flags two pre-existing low-severity findings (missing `concurrency:` on both `ci.yml` and `dependency-review.yml`) — unrelated to this change and present before it, so I left them alone.

**Diagnosis:** not the harden-runner version. Same `egress-policy: block`, same allowed-endpoints list in both the passing and failing runs. The failing log shows `domain not allowed: api.deps.dev.` — this PR modifies `requirements.txt`, so `dependency-review-action` now calls deps.dev for package data, and that host was never in the allowlist. The previous PR that passed didn't touch a manifest, so it never hit that code path.

**Fix applied:** added `api.deps.dev:443` to `allowed-endpoints` in `.github/workflows/dependency-review.yml`. The harden-runner pin stays at v2.21.0.

This is an egress-allowlist change, so per the skill's own rule it's behavioral, not structural — I can't confirm it's fixed without a run. It's unverified until the check re-runs on this PR (which does change `requirements.txt`, so it will exercise the new endpoint). I did not push or trigger a workflow run.

**File changed:** `.github/workflows/dependency-review.yml`

Not committing — say if you want that done.
