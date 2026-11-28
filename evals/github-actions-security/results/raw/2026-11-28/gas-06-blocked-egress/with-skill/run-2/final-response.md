I didn't roll back the pin, because the logs show `harden-runner` v2.21.0 didn't cause this failure. The job blocks outbound traffic, and your allowlist is missing a host it now needs. I added that host in `.github/workflows/dependency-review.yml`:

```diff
           allowed-endpoints: >
+            api.deps.dev:443
             api.github.com:443
```

**What happened**
- The failing log's post-step says `domain not allowed: api.deps.dev.`
- This pull request changes `requirements.txt`. The last passing run was on a pull request that changed no dependency manifest, and its log never mentions `api.deps.dev`.
- In the `dependency-review-action` v5.0.0 source (`src/scorecard.ts`), the action calls `api.deps.dev` when a changed dependency has no source repository URL from GitHub. That call has no error handling, so a block fails the step with just `fetch failed`.
- The allowlist is the same in both logs. The passing run used `bf7454d…`, which is v2.20.0, and the current pin `05e3151…` is v2.21.0.

So going back to v2.20.0 would keep the same allowlist and, as far as these logs show, fail the same way. The months of passes don't rule this out, since only runs that reach that lookup need the host.

**Checks**
- `actionlint` passes.
- `zizmor` 1.31.1, run offline, reports two low-severity `concurrency-limits` findings, one in each workflow. They aren't from this edit, so I left them.
- **The fix is not yet verified on a runner.** I haven't committed or pushed anything.

**To get the check green**
1. Commit and push the change to your pull request branch. This checkout is on `main` with no remote configured, so apply it on the PR branch.
2. Check that the new Dependency Review run on that pull request passes. It changes `requirements.txt`, so it should reach the same lookup.
3. If it still fails, look for another `not allowed` line in the Harden Runner post-step. `codeload.github.com` also appears in the failing log as resolved, though not as blocked or connected to, and it isn't on your allowlist.

Suggested pull request note: "Allow `api.deps.dev:443` in Dependency Review. `dependency-review-action` needs it for some Scorecard lookups when dependencies change."

This lets the job reach one more external host. If you'd rather not allow that, setting `show-openssf-scorecard: false` on the action should skip the lookup, but you'd lose the Scorecard information.

**Newer releases**
`harden-runner` is now at v2.23.0 (released 2026-11-18), and `dependency-review-action` has a v5.0.1 tag. I didn't change either, to keep this fix to one cause; they're worth a separate update.

If you still want v2.20.0 for another reason, change both the SHA to `bf7454d06d71f1098171f2acdf0cd4708d7b5920` and the comment to `# v2.20.0`. Keep the new allowlist line either way. `ci.yml` uses the same v2.21.0 pin.
