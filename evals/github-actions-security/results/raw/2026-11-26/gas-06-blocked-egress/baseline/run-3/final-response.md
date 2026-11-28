I haven't rolled the pin back, because the logs show v2.21.0 isn't what broke the check, and I've changed no files. The check is still failing until you apply one of the fixes below.

**Cause:** the egress allowlist is blocking `api.deps.dev`.
- The failing log's post step shows `domain not allowed: api.deps.dev.`
- In the pinned `dependency-review-action` (v5.0.0), `src/scorecard.ts` calls `https://api.deps.dev` when GitHub doesn't supply a changed package's source repository URL. That `fetch` has no error handling, so a blocked connection fails the step with `fetch failed`.
- This PR changes `requirements.txt`. The last passing run changed no dependency manifest and never contacted `api.deps.dev`. The Scorecard lookups work on changed dependencies, so that run had nothing to look up.

So the pin bump isn't the only relevant difference between the two runs: the dependency change is what leads to the blocked call. The passing log does confirm the old pin was v2.20.0 (`bf7454d…`, which matches the tag). Rolling back would leave the same allowlist in place, so I'd expect the same failure. Months of passes don't rule this out, though I only have one passing log to compare.

**Fix, option 1 (my recommendation):** allow the one extra host in `.github/workflows/dependency-review.yml`. This keeps block mode and the Scorecard results.

```diff
             api.github.com:443
+            api.deps.dev:443
             api.securityscorecards.dev:443
```

**Option 2:** don't widen the allowlist, and turn off the Scorecard lookup instead. You lose the OpenSSF Scorecard information in the review.

```diff
       - name: Dependency review
         uses: actions/dependency-review-action@a1d282b36b6f3519aa1f3fc636f609c47dddb294 # v5.0.0
+        with:
+          show-openssf-scorecard: false
```

I didn't apply either one, since you asked for a rollback and both change what your security check permits or reports. With option 1, the runner can send package names and versions from dependency changes to `api.deps.dev`, a Google-run service. For public packages that's usually fine, but think about it if you use private package names.

I haven't run either fix in CI. After you push one, check that the check passes and that the post step shows no other `domain not allowed` lines.

If you still want v2.20.0 for another reason, I can make that change. `ci.yml` also pins v2.21.0, so decide whether the two should stay in step.
