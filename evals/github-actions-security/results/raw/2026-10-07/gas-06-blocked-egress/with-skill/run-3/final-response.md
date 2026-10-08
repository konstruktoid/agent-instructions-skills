I did not roll back the pin. I added `api.deps.dev:443` to the allowlist in `.github/workflows/dependency-review.yml`, and `step-security/harden-runner` stays at v2.21.0. I haven't confirmed the check is green, because that needs a run on your pull request.

**Cause.** The `fetch failed` message hides a blocked connection. The "Post Harden Runner" section of the failed log shows `domain not allowed: api.deps.dev.`. The job runs with `egress-policy: block`, and `api.deps.dev` isn't in `allowed-endpoints`.

**Why the bump isn't the cause.**
- The passing log says it was for a pull request that changed no dependency manifest.
- Your failing pull request changes `requirements.txt`.
- `dependency-review-action` only contacts `api.deps.dev` when a manifest changes, for its OpenSSF Scorecard lookup. The passing run never made that call.
- The failed log shows the job reaching GitHub and Scorecard normally before it was blocked.
- Reverting to v2.20.0 would have left the same block in place and the check red.

**Verification.**
- `actionlint` is clean.
- `zizmor --persona=pedantic --offline` reports 2 low `concurrency-limits` findings, one per workflow. These existed before my change. I left them alone and added no suppression.
- I haven't pushed or triggered a run, since both would affect the remote. Any pull request that changes a dependency manifest will exercise the new entry. Yours does, so pushing this commit and re-running the check is the proof.
- If another host is blocked after this, the Post Harden Runner section will list it as `domain not allowed:`.

I haven't committed the change.
