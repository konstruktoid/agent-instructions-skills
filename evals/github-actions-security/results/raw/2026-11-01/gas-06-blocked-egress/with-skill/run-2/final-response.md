I didn't roll back the pin. I added `api.deps.dev:443` to the allowlist in `.github/workflows/dependency-review.yml` and left harden-runner at v2.21.0. I haven't run the fix, so I don't know yet that the check goes green.

**Why the rollback wouldn't fix it**
- **Cause:** The failing log's "Post Harden Runner" section says `domain not allowed: api.deps.dev.`. The `fetch failed` error is the dependency-review action's generic message for that blocked connection.
- **Why only this PR:** The action only contacts `api.deps.dev` when a PR changes a dependency manifest, and this PR changes `requirements.txt`. The last green run changed no manifest, so it never made that call. The old allowlist was missing the host all along, and no earlier PR exercised it.
- **The pin:** v2.20.0 would hit the same block on this PR.

**Checks**
- `actionlint` is clean.
- `zizmor` (pedantic) reports only two low "missing concurrency" notes, one in `ci.yml` and one in `dependency-review.yml`. Both were already there and have nothing to do with this change. I left them alone.
- **Not verified:** I didn't push or trigger a run, since that has effects outside this working copy. A push to this PR's branch will re-run the check, and I expect it to pass. That is the only thing that will confirm the allowlist is now complete.
- **Still open:** If the log then names another blocked host, add it the same way.

I haven't committed anything. The change is one line in the working tree.
