I didn't roll back the pin, because the bump isn't what broke the check. I added `api.deps.dev:443` to the egress allowlist instead. I haven't run the check on the pull request, so that fix is untested on a runner.

**What the logs show**
- In the failed log, the `Post Harden Runner` section says `domain not allowed: api.deps.dev.`. The `fetch failed` error in the dependency-review step is that blocked connection.
- `actions/dependency-review-action` only calls `api.deps.dev` for its OpenSSF Scorecard lookup, and only when a pull request changes a dependency manifest.
- Your last passing pull request changed no manifest, so that call never happened and the host never showed up in the allowlist. This pull request changes `requirements.txt`, so the call happened and was blocked.
- Rolling back to v2.20.0 would leave `block` mode as it is, so the same host would still be blocked.

**The change**
In `.github/workflows/dependency-review.yml`, I added `api.deps.dev:443` to `allowed-endpoints`, with a comment saying when it's contacted. The harden-runner pin stays at v2.21.0, and `egress-policy: block` is unchanged.

**Checks**
- `actionlint` is clean.
- `zizmor --persona=pedantic` reports two low `concurrency-limits` findings, one in `ci.yml` and one in `dependency-review.yml`. Both workflows have no `concurrency` setting. I left them alone because they're unrelated to this failure, and I can add the settings if you want.
- **Not verified on a runner.** A pull request that changes a dependency manifest would test it, and this one does. Push the change and re-run the check. If it still fails, check the `Post Harden Runner` section for another `domain not allowed:` line. The action may need other hosts that this run never got far enough to try.

I haven't committed or pushed anything.
