I didn't roll back harden-runner, because the logs show v2.21.0 isn't what broke the check. Instead I added `api.deps.dev:443` to the allowlist in `.github/workflows/dependency-review.yml`. The change is uncommitted and not pushed, so the check isn't confirmed green yet.

**Cause.** The failing job's `Post Harden Runner` section says:

```
domain not allowed: api.deps.dev.
```

The job blocks outbound connections to anything not on the list, and `dependency-review-action` only reported that as `fetch failed`.

**Why it started on this pull request**
- This pull request changes `requirements.txt`. The action contacts `api.deps.dev` to look up OpenSSF Scorecard data when dependencies change.
- The last passing run changed no dependency manifest. Its log shows no lookup of `api.deps.dev` or `api.securityscorecards.dev`, so it never reached this code.
- The action is pinned to the same commit in both runs, and so is the allowlist.

The harden-runner bump appears to be coincidental. Going back to v2.20.0 would leave `api.deps.dev` off the list, so I'd expect the same failure. I only have one passing log, so I can't say what earlier green runs touched.

**The fix**

```diff
           allowed-endpoints: >
+            api.deps.dev:443
             api.github.com:443
```

This lets the job reach one more host. If you'd rather not allow it, you can set `show-openssf-scorecard: false` on the dependency review step. That should avoid the lookup, but you lose the Scorecard information, and I haven't tested it.

**Checks**
- **`actionlint`:** passed.
- **`zizmor` (offline, pedantic):** two low `concurrency-limits` findings, one in `ci.yml` and one in `dependency-review.yml`. They concern settings my edit didn't touch, so I left them.
- **Action versions:** I couldn't check whether the pins are current or match their release tags, because `gh` isn't logged in. I changed no pins.

**To confirm it**
Commit and push this to the pull request branch. This checkout only has `main` and no remote, so make sure the edit lands on the right branch. The new run on your pull request will exercise the fix, since it changes `requirements.txt`.

If it still fails, look in `Post Harden Runner` for another `domain not allowed` line, because the job may get further and reach a new host:

```sh
gh run view --job <job-id> --log | grep -i "not allowed"
```

If `api.deps.dev` is allowed, nothing else is blocked and it still fails, then the version bump is worth another look.
