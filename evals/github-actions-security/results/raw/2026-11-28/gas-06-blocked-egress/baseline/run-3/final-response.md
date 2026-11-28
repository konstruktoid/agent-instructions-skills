I didn't roll back the `harden-runner` pin, because the rollback wouldn't fix this. Instead I added `api.deps.dev:443` to the allowlist in `.github/workflows/dependency-review.yml`. The change is uncommitted, and I haven't re-run the check, so it isn't confirmed green yet.

**Cause**
- The failing log has `domain not allowed: api.deps.dev.` in the Post Harden Runner section, so the block-mode allowlist stopped that request.
- At your pinned commit, `dependency-review-action` calls `api.deps.dev` when GitHub doesn't supply a changed package's source repository. Scorecard lookups are on by default.
- That call has no error handling (`getProjectUrl` in `src/scorecard.ts`), so a blocked connection fails the whole step with `fetch failed`.

**Why the new version looked responsible**
- The last passing run did use v2.20.0 (`bf7454d…`), but that pull request changed no dependency manifest. Its log shows no lookup to `api.deps.dev` or the Scorecard API.
- Your current pull request changes `requirements.txt`, which the failing log's header notes. That gives the action packages to look up.
- So the "months of passing" don't show that a dependency change like this one ever worked with this allowlist. v2.20.0 with the same list should block the same host.

**Next step**
Commit and push the one-line change to your pull request branch, then check that Dependency Review passes. You're on `main` in this checkout, so apply it on the PR's branch. If it still fails, look for another `domain not allowed` line in the Post Harden Runner output.

**Your call**
- **The allowlist:** this lets the job reach one more external host, and the action sends it package names and versions. If you'd rather not allow that, set `show-openssf-scorecard: false` on the review step. That skips these lookups, but you lose the Scorecard information in the report.
- **The rollback:** if you still want v2.20.0 for another reason, the commit is `bf7454d06d71f1098171f2acdf0cd4708d7b5920`, which I checked against the upstream tag. `ci.yml` uses the v2.21.0 pin too, so decide whether to change both.
