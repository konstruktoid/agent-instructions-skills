I didn't roll the pin back, because the logs show the v2.21.0 bump didn't break the check. I added the endpoint the check was missing to the egress allowlist instead. I haven't run the check, so it isn't confirmed green.

**Cause.** The harden-runner post-step in `ci-logs/dependency-review-failed.log` says `domain not allowed: api.deps.dev.` The job runs with `egress-policy: block`, so the dependency-review action's connection to that host was refused. The action surfaced that as `fetch failed`.

**Why it looked like the bump.** The passing run was on a pull request that changed no dependency manifest. This pull request changes `requirements.txt`. The action only calls `api.deps.dev` (for its Scorecard lookup) when a manifest changes. The earlier passing runs never reached that call, so the endpoint was never in the allowlist. Rolling back to v2.20.0 would not have fixed it.

**Change.** In `.github/workflows/dependency-review.yml` I added `api.deps.dev:443` to `allowed-endpoints`. The pin stays at v2.21.0.

**Checks**
- `actionlint` is clean.
- `zizmor` reports 2 low findings, both "no concurrency limit" (`concurrency-limits`), one in `dependency-review.yml` and one presumably in `ci.yml`. I only saw the first in the output. They were already there and have nothing to do with this fix. I left them alone and added no suppression.
- The fix is unverified until a run exercises it. I didn't push, because that changes a remote branch and you didn't ask for it. Pushing to this pull request will trigger the run, and it already changes `requirements.txt`, so it will hit the `api.deps.dev` path. If the run still fails, check the post-step for another `domain not allowed:` line. The action may need other hosts on that path.

Do you want me to commit and push?
