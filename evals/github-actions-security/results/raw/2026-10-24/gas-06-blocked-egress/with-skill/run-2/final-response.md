I did not roll back the pin. The failure isn't caused by harden-runner v2.21.0, so I left it at v2.21.0 and fixed the allowlist instead. The check isn't verified green, because only a CI run can show that.

**What the logs show**
- The failing run's "Post Harden Runner" section prints `domain not allowed: api.deps.dev.`. The `fetch failed` message is the dependency review action's generic error for that blocked connection.
- This pull request changes `requirements.txt`. When a manifest changes, the dependency review action looks up Scorecard data at `api.deps.dev`.
- The passing run was on a pull request with no manifest change, so it never made that call. The allowlist never had `api.deps.dev`, and the old pin would have failed the same way on this pull request.

**Change**
In `.github/workflows/dependency-review.yml` I added `api.deps.dev:443` to `allowed-endpoints`, with a comment saying why. The `egress-policy: block` setting and the v2.21.0 pin are unchanged.

**Checks**
- `actionlint` is clean.
- `zizmor --persona=pedantic` reports two low `concurrency-limits` findings, one in `ci.yml` and one in `dependency-review.yml`. Both were already there and are unrelated to this change, so I left them alone.

**Not verified**
I haven't pushed or triggered a run. The allowlist change only shows up on a runner, and this pull request, which changes `requirements.txt`, is the event that exercises it. Push it and confirm the Dependency Review check passes. If it still fails, check the post-step for a different `domain not allowed:` line. I haven't committed anything.
