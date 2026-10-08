I haven't rolled back the harden-runner pin. I added `api.deps.dev:443` to the egress allowlist in `.github/workflows/dependency-review.yml` and left `step-security/harden-runner` at v2.21.0. I haven't pushed anything, so the check hasn't run again.

**Why the pin isn't the cause**
- The harden-runner post-step in the failed log says `domain not allowed: api.deps.dev.` The `fetch failed` line is what the dependency-review action reports when that connection is blocked.
- Your pull request changes `requirements.txt`. That makes the action look up OpenSSF Scorecard data through `api.deps.dev`.
- The last passing run was on a pull request with no manifest change. That run never called `api.deps.dev` or `api.securityscorecards.dev`, so it never exercised this path. The allowlist has always lacked `api.deps.dev`.
- Reverting to v2.20.0 would most likely have failed the same way, and it would have left you on an older release for no reason.

**Verification**
- `actionlint` is clean.
- `zizmor` reports two low-severity `concurrency-limits` findings, one in `ci.yml` and one in `dependency-review.yml`. These were there before my change and I left them alone.
- This fix is unverified until a run exercises it. A pull request that changes a dependency manifest, such as this one, will do that. Please push the change and watch the check. If it still fails, read the harden-runner post-step for another `domain not allowed:` line.
