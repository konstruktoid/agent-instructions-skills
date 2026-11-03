I haven't changed anything yet. The v2.21.0 pin isn't what's breaking the check, so rolling it back to v2.20.0 wouldn't turn it green.

**What the logs show**
- The failed log has `domain not allowed: api.deps.dev.` in the Harden Runner post-step. The egress policy is `block`, and `api.deps.dev:443` isn't in `allowed-endpoints` in `.github/workflows/dependency-review.yml`.
- The action's `fetch failed` is that blocked request.
- The passing run was on a PR that changed no dependency manifest. It only called `github.com` and `api.github.com`.
- This PR changes `requirements.txt`, so `dependency-review-action` now looks up the new packages on `api.deps.dev`. That's why it has passed for months and fails now.
- The passing log used a different harden-runner SHA, but both runs enforce the same block policy. Neither run had `api.deps.dev` allowed.

**Proposed fix**
Add `api.deps.dev:443` to `allowed-endpoints` in `dependency-review.yml`. I'd keep the v2.21.0 pin.

I haven't made this edit because it widens your egress allowlist, which is a security control. Do you want me to add it? I can also do the v2.20.0 rollback in addition if you still want it. It would be a separate change, and I'd have to look up and verify the v2.20.0 commit SHA, since I can't check it from here.

I can't run the check from here, so I can't confirm it goes green until it runs on CI. If the new endpoint is the only block, it should.
