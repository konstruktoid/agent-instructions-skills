I didn't roll back harden-runner, because the logs show v2.21.0 isn't what broke the check. Instead I added `api.deps.dev:443` to the allowlist in `.github/workflows/dependency-review.yml`. The change isn't committed or pushed, so the check hasn't been re-run and I can't yet say it's green.

**Cause**
- The failing log says `domain not allowed: api.deps.dev.`, so your egress block policy stopped the request, and that surfaced as `fetch failed`.
- In `dependency-review-action` v5.0.0, `src/scorecard.ts` calls `api.deps.dev` when a changed dependency has no source repository URL from GitHub. That call has no error handling, so a blocked request fails the step.
- The last passing run was on a pull request that changed no dependency manifest, and its log shows no lookup to `api.deps.dev`. Your current pull request changes `requirements.txt`.

So the pin change and the failure showing up together looks like coincidence. Rolling back to v2.20.0 would keep the same block policy and allowlist, so I'd expect the same failure. I confirmed that your two SHAs match the upstream v2.20.0 and v2.21.0 tags, but I didn't review what changed between those releases.

**The change**
```diff
             api.github.com:443
+            api.deps.dev:443
             api.securityscorecards.dev:443
```

This loosens your egress policy by one host, so it's worth a deliberate look. The action sends `api.deps.dev` the ecosystem, name and version of some changed dependencies. If you'd rather not allow that, setting `show-openssf-scorecard: false` on the action should skip these lookups, but you'd lose the Scorecard information in the review.

**Next step**

Commit and push this to your pull request branch and let the check run again. The local checkout only has `main`, so make sure the commit goes on the right branch. If it still fails, look in the "Post Harden Runner" section for another `domain not allowed` line.

If you still want v2.20.0 for some other reason, the pin would be `step-security/harden-runner@bf7454d06d71f1098171f2acdf0cd4708d7b5920 # v2.20.0`. Keep the allowlist line either way. `ci.yml` also uses v2.21.0, in audit mode.
