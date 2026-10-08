I added `api.deps.dev:443` to the egress allowlist in `.github/workflows/dependency-review.yml`. I did not roll back the harden-runner pin, because the logs show it isn't the cause. I haven't pushed this or seen the check run, so it isn't confirmed green yet.

**Cause**
- The failing log's Post Harden Runner section says `domain not allowed: api.deps.dev.` The runner is in `egress-policy: block`, so the dependency-review action's request to deps.dev was refused. The action reports that as `fetch failed`.
- The passing run was on a PR that changed no dependency manifest. The action never called deps.dev there. This PR changes `requirements.txt`, so the action now looks up the changed packages on deps.dev. That also explains why the check has passed for months.
- Both runs show the same egress policy and allowlist, and both were in block mode. The pin change doesn't explain the failure. Rolling back to v2.20.0 would leave `api.deps.dev` blocked, so the check would still fail.

**Next steps**
- Push this change and re-run the check to confirm it passes. I can't run it from here.
- I can still roll the pin back in both `dependency-review.yml` and `ci.yml` if you want. I'd leave it, since nothing in the logs implicates v2.21.0.
- The post-step log also lists `codeload.github.com` as resolved. Nothing blocked it, so I left it out. If a later run reports it as `domain not allowed`, add it to the allowlist too.
