I didn't roll back `harden-runner`, because the logs show v2.21.0 isn't what broke the check. Your egress allowlist is missing `api.deps.dev:443`, and I added that line to `.github/workflows/dependency-review.yml`. The check isn't green yet: the change is uncommitted and hasn't run on GitHub.

**Why it failed**
- The failed job's `Post Harden Runner` section says `domain not allowed: api.deps.dev.` The `fetch failed` message just doesn't name the host.
- The dependency review action calls `api.deps.dev` in `src/scorecard.ts`, at the exact commit you have pinned (v5.0.0).
- This pull request changes `requirements.txt`. The last passing one changed no dependency manifest, and its log shows no lookup of `api.deps.dev` or `api.securityscorecards.dev`. So that run never reached this code.
- `api.deps.dev` wasn't on the allowlist under v2.20.0 either, so rolling back should fail the same way.

I confirmed that both SHAs in your logs match their tags: `bf7454d` is v2.20.0 and `05e3151` is v2.21.0.

**What to do next**
My checkout is on `main`, so make sure this line lands on your pull request branch:

```yaml
          allowed-endpoints: >
            api.deps.dev:443
```

Pushing it should start a new run; re-running the old job would still use the old allowlist. Because your pull request changes `requirements.txt`, that run will exercise the blocked call. If it still fails, look for another `domain not allowed:` line in the same post-step section.

This does allow one more outbound destination from that job. It's limited to the host the action needs, and blocking stays on.

**Checks**
- `actionlint` passes.
- `zizmor` 1.31.1, run offline with the pedantic setting, reports two low `concurrency-limits` findings and exits 12. They concern the missing `concurrency` setting in `ci.yml` and `dependency-review.yml`, not the line I added, so I left them.

**Separate from this fix:** newer `harden-runner` tags exist, up to v2.23.0. I didn't check their release dates or notes, and upgrading wouldn't fix this failure.

If you still want the rollback for another reason, it's a one-line change to `bf7454d06d71f1098171f2acdf0cd4708d7b5920 # v2.20.0`, but keep the `api.deps.dev` line either way.
