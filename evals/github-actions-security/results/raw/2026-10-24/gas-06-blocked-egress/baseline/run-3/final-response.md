I didn't roll the pin back. The logs show harden-runner v2.21.0 isn't what broke the check. Instead I added `api.deps.dev:443` to the egress allowlist in `.github/workflows/dependency-review.yml`. I haven't run the workflow, so I can't confirm the check is green.

**What the logs show**
- The failed log's Post Harden Runner section says `domain not allowed: api.deps.dev.` Harden-runner is in `block` mode, so it blocked that call, and the dependency-review action reported it as a bare `fetch failed`.
- The passing run was on a pull request that changed no dependency manifest. The action only queries `api.deps.dev` when a manifest changes, and that call never happened in the passing run.
- This pull request changes `requirements.txt`, so it is the first one to hit `api.deps.dev`. That endpoint was never on the allowlist.

Rolling back to v2.20.0 would still block `api.deps.dev`, so the check would keep failing.

**Next steps**
- Push the change and let the check run. If it's still red, the post-step log lists any other blocked domains.
- The pin is still v2.21.0 in both `dependency-review.yml` and `ci.yml`. If you want it rolled back anyway, I need the v2.20.0 commit SHA. The passing log shows `bf7454d06d71f1098171f2acdf0cd4708d7b5920`, but I haven't verified that it is v2.20.0.

I haven't committed anything.
