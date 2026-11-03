I did not roll back the pin. I added `api.deps.dev:443` to the egress allowlist in `.github/workflows/dependency-review.yml` and kept `harden-runner` at v2.21.0. I haven't pushed or run the check, so the fix is unverified.

**Cause**
- The "Post Harden Runner" section of the failing log says `domain not allowed: api.deps.dev.` That is the real error behind `fetch failed`.
- The passing log has no `api.deps.dev` lookup at all. That earlier PR changed no dependency manifest.
- This PR changes `requirements.txt`. That makes `dependency-review-action` look up `api.deps.dev` for its OpenSSF Scorecard data, and `egress-policy: block` rejected the connection.
- Rolling back to v2.20.0 would not have helped. The allowlist would still lack `api.deps.dev`, and the check would still fail on any PR that touches a manifest.

**Checks**
- `actionlint` isn't installed here, so I didn't run it.
- `zizmor` reported 2 low "missing concurrency" findings, run offline. I didn't touch them.
- A real run is the only proof. Push the branch, or re-run the check on this PR, and confirm `api.deps.dev` now shows as an allowed call in the post-step log. Any PR that changes a manifest exercises the same path.

If the check still fails, check the post-step log for another `domain not allowed:` line. The action might call other hosts that this log didn't reach, since it stopped at the first blocked call.

I made the change in the working tree but did not commit.
