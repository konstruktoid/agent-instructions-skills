I did not roll back the pin. I added `api.deps.dev:443` to the egress allowlist in `.github/workflows/dependency-review.yml` instead. The change is uncommitted and nothing has been pushed.

**Why the pin isn't the cause**
- The failing log's "Post Harden Runner" section says `domain not allowed: api.deps.dev.` The step's own `fetch failed` message hides this. The dependency review action tried to reach `api.deps.dev` and the `block` egress policy refused it.
- The action only calls `api.deps.dev` when a PR changes a dependency manifest, for its Scorecard lookup. Your failing PR changes `requirements.txt`.
- The last passing run was on a PR that changed no manifest, so it never made that call. That is why the check passed for months.
- The two runs' `endpoint called` lines show the same thing: the passing run never contacted `api.deps.dev`.
- Reverting to v2.20.0 would have left the same failure in place. The v2.21.0 bump just happened to land in the same PR.

**Verification**
- `actionlint` is clean.
- `zizmor` (pedantic) reports only two low `concurrency-limits` findings, in `ci.yml` and `dependency-review.yml`. Neither is related to this change, and I left them alone.
- The check is **not yet verified green**. The allowlist change is behavioral, and only a run on a PR that changes a dependency manifest will exercise it. Your current PR does, so pushing this change will re-run the check. I didn't push, because that changes a remote branch. Tell me if you want me to push it.

If the check still fails after the push, the new post-step log will show the next blocked domain. The log should also show whether the dependency review action needs a further endpoint.
