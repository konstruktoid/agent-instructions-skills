I didn't roll back the harden-runner pin, because the new version isn't what broke the check. I added `api.deps.dev:443` to the allowlist in `.github/workflows/dependency-review.yml` instead. The change isn't committed or pushed, so the check on your PR is still red until you do that.

**Cause**

The failing log's "Post Harden Runner" section shows what `fetch failed` hid:

```
domain not allowed: api.deps.dev.
```

- **Why it appeared now:** your PR changes `requirements.txt`. The last passing run was on a PR that changed no dependency manifest, and its log never looks up `api.deps.dev`.
- **Where the call comes from:** in the pinned `dependency-review-action` v5.0.0, `src/scorecard.ts` queries `api.deps.dev` when GitHub doesn't supply a dependency's repository URL.
- **Why the old pass doesn't clear v2.20.0:** that run did use v2.20.0, but it never reached this call. With the same allowlist, rolling back should fail the same way.

**Checks**

- `actionlint` passed.
- `zizmor` 1.31.1, run offline, reported two low `concurrency-limits` findings, one each in `ci.yml` and `dependency-review.yml`. They concern lines I didn't change, so I left them.
- The allowlist fix itself is **unverified**. Only a run on a PR that changes a dependency manifest, such as yours, can prove it.

**Next step**

Commit and push the change to your PR branch, or ask me to. If it still fails, look at the same post-step section for another `domain not allowed:` line.

**If you'd rather not allow the host**

You could set `show-openssf-scorecard: false` on the dependency review step. That should avoid the call, but you'd lose the Scorecard summary and its warnings. I kept the feature and allowed the one host.

If you still want v2.20.0 for another reason, I can make that change, but keep the allowlist entry. `ci.yml` also pins v2.21.0, so decide whether it should move too. `gh` isn't logged in here, so I didn't check whether a newer harden-runner release exists.
