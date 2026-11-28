I didn't roll back the pin, because the new Harden Runner version isn't what broke the check. The job's egress allowlist is missing `api.deps.dev`. I added it in `.github/workflows/dependency-review.yml`:

```diff
             api.github.com:443
+            api.deps.dev:443
             api.securityscorecards.dev:443
```

**Why it fails**
- The failing log's post step says `domain not allowed: api.deps.dev.`
- In `dependency-review-action` v5.0.0 (the SHA you pin), `src/scorecard.ts` calls `api.deps.dev` when a changed dependency has no source repository URL from GitHub. That `fetch` has no error handling, so a blocked connection fails the step with `fetch failed`.
- Your pull request changes `requirements.txt`. The last passing run changed no dependency manifest, and its log shows no lookup of `api.deps.dev` or `api.securityscorecards.dev`. Months of passing runs therefore don't show that this path worked under the allowlist.

**Why not roll back:** v2.20.0 would run with the same `block` policy and allowlist, so I'd expect the same failure, and you'd lose the upgrade for nothing. I checked that the two SHAs in your files and logs match the v2.20.0 and v2.21.0 tags.

**What this loosens:** the job can now also connect to `api.deps.dev` on port 443. That's Google's Open Source Insights API, and the action sends it the ecosystem, package name and version of dependencies it looks up. If you'd rather not allow that, set `show-openssf-scorecard: false` on the dependency review step instead. This should skip the lookup, but you'd lose the Scorecard summary.

**Not yet verified:** the change is uncommitted and unpushed, and I haven't seen the check pass. Commit and push it to your pull request branch (the local checkout is on `main`, so check that first), then let the check rerun. If it still fails, look for another `domain not allowed` line in the post step.

If you still want the pin rolled back for some other reason, I can do that, but keep the allowlist line either way.
