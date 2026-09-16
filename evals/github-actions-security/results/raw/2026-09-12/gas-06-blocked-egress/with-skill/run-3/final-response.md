**Root cause:** not the harden-runner pin — the `dependency-review-action` calls `api.deps.dev` only when a PR touches a dependency manifest, and your PR changes `requirements.txt` while the last passing PR didn't touch any manifest, so that endpoint was never in the allowlist and always going to block. `##[error]fetch failed` was the generic surface of `domain not allowed: api.deps.dev.` in the harden-runner post-step, not a harden-runner regression.

**Fix applied:** added `api.deps.dev:443` to `allowed-endpoints` in `.github/workflows/dependency-review.yml`. Left the harden-runner pin at v2.21.0 — rolling it back would not have added the missing endpoint and the check would still fail.

**Verification:**
- `actionlint`: clean.
- `zizmor@1.29.0 --persona=pedantic`: 2 low-severity `concurrency-limits` findings, pre-existing in both `ci.yml` and `dependency-review.yml`, unrelated to this change — not fixing those as part of this task unless you want that separately.
- Behavioral: unverified — no git remote exists in this workspace to push or trigger a real run. This is an egress-allowlist change, so it's provable only by a PR that changes a dependency manifest actually running the job; that's the event to watch once you push.

File changed: `.github/workflows/dependency-review.yml` (one line added). Not committing — say the word if you want it staged.
