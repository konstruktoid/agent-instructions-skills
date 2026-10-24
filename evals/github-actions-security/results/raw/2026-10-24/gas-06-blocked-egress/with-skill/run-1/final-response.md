I didn't roll back the pin. The `harden-runner` bump isn't what broke the check, so I left it at v2.21.0 and fixed the real cause.

**Cause:** your workflow runs `harden-runner` with `egress-policy: block`. Near the end of the failing log, the "Post Harden Runner" section prints `domain not allowed: api.deps.dev.` The `fetch failed` message is just the dependency-review action's generic error when that connection is blocked. The action only contacts `api.deps.dev` when a pull request changes a dependency manifest. This pull request changes `requirements.txt`, and the earlier passing runs never touched a manifest. The passing log has no `api.deps.dev` lookup at all, so the old pin was never tested on this path. Rolling back to v2.20.0 would most likely have left the check failing.

**Change:** I added `api.deps.dev:443` to `allowed-endpoints` in `.github/workflows/dependency-review.yml`. The `harden-runner` pin stays at v2.21.0.

**Verification:**
- **`actionlint`:** it printed nothing, so it is clean.
- **`zizmor`:** it reports two low "missing concurrency" findings, one for this workflow and one for `ci.yml`. They were already there and have nothing to do with this fix, so I left them alone.
- **The check itself:** not yet verified. Whether the check goes green can only be confirmed by a run on a pull request that changes a manifest, and I haven't pushed anything. This pull request is that case, so pushing the fix to its branch will test it.

If it still fails, look at the post-step output for another `domain not allowed:` line. The failing log also resolved `codeload.github.com` but never connected to it, so it is not currently needed.

I haven't committed anything.
