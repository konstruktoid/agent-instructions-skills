I didn't roll back the pin. The logs show the v2.21.0 bump isn't what broke the check, so a rollback wouldn't turn it green. I added one allowed endpoint instead. I couldn't run CI from here, so the check hasn't been re-run.

**What the logs show**
- The failed run's Harden Runner summary has the line `domain not allowed: api.deps.dev.`. The runner is in `egress-policy: block`, and `api.deps.dev` isn't in `allowed-endpoints`. That blocked call is what surfaces as `fetch failed`.
- The passing run was on a pull request that changed no dependency manifest. Your current pull request changes `requirements.txt`. `dependency-review-action` only calls `api.deps.dev` when a manifest changes, so earlier runs never hit the block.
- v2.20.0 would block the same call, because the allowlist is identical in both runs.

**The change**
In `.github/workflows/dependency-review.yml` I added `api.deps.dev:443` to `allowed-endpoints`. Both `harden-runner` pins (that file and `ci.yml`) are still at v2.21.0.

Adding the endpoint widens your egress allowlist, so check you're happy with that. It's the host the action needs for dependency lookups.

Re-run the check on the pull request to confirm. If it still fails, send me the new log. If you still want the pin back at v2.20.0 for other reasons, tell me and I'll change it in both workflows.
