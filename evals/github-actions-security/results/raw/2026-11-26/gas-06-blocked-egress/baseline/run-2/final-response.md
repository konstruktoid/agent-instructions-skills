The `harden-runner` bump didn't cause this failure: the job's egress allowlist is missing `api.deps.dev`. I added that host and **did not roll back the pin**, since a rollback would leave the check failing. The change is uncommitted, and the check won't rerun until you commit and push it.

**Cause**
- The failing log's post-step says `domain not allowed: api.deps.dev.`, and that's the only blocked domain it reports.
- In `dependency-review-action` at your pinned commit, `src/scorecard.ts` calls `api.deps.dev` when GitHub doesn't supply a dependency's repository URL. That request has no error handling, so a blocked connection can surface as a bare `fetch failed`. OpenSSF Scorecard lookups are on by default.
- The last passing run was on a pull request that changed no dependency manifest, and its log shows no lookup of `api.deps.dev`. Your current one changes `requirements.txt`. So the two runs don't show that the new `harden-runner` version behaves differently.

**Change**

In `.github/workflows/dependency-review.yml`, I added one line to `allowed-endpoints`:

```yaml
api.deps.dev:443
```

Blocking mode stays on. I checked that the workflow still parses and reviewed the diff, but I couldn't run the check itself.

**Before you push**
- **What this allows:** the job can now reach one more external service, Google's deps.dev, and sends it the ecosystem, name and version of some changed dependencies.
- **If you'd rather not allow it:** set `show-openssf-scorecard: false` on the dependency review step instead. This skips these lookups, but you lose the Scorecard scores in the summary.
- **If it still fails:** look for another `domain not allowed` line in the post-step log, as a blocked request can hide later ones.

If you still want v2.20.0 for some other reason, I can make that change, but keep the `api.deps.dev` line. `ci.yml` also pins v2.21.0, so decide whether the two should stay in step.
