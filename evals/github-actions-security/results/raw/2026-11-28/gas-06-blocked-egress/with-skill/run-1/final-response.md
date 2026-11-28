**I didn't roll back the pin, because the new Harden Runner version isn't what broke the check.** The egress allowlist is missing a host, and I added it in `.github/workflows/dependency-review.yml`. The change isn't committed or pushed, so I haven't confirmed the check goes green.

**Cause**

The post-step of your failing log (`ci-logs/dependency-review-failed.log`) has this line:

```
domain not allowed: api.deps.dev.
```

- **Why this PR hits it:** it changes `requirements.txt`. The dependency review action contacts `api.deps.dev` when a dependency manifest changes.
- **Why it passed before:** the last passing run was on a PR that changed no manifest, and its log never looks up `api.deps.dev`. That run doesn't show v2.20.0 allowing the host; it never tried to reach it.
- **Why a rollback wouldn't help:** both logs show the same allowlist in `block` mode, and v2.20.0 would have the same missing entry.

I only have one passing log, so I can't tell whether earlier PRs that changed a manifest ran this check.

**Fix**

I added `api.deps.dev:443` to `allowed-endpoints`, with a short comment explaining why. Blocking stays on, and the pin stays at v2.21.0.

**Checks**

- **`actionlint`:** passes.
- **`zizmor` 1.31.1 (pedantic, offline):** reports two low-severity `concurrency-limits` findings, one in each workflow. Neither comes from this edit, so I left them.
- **Pins:** the public tags confirm that `05e3151…` is v2.21.0 and that the passing log's `bf7454d…` is v2.20.0.
- **Not checked:** `gh` isn't logged in, so I didn't check the latest releases or the other actions' pins.

**Next step**

Commit and push this to your PR branch; the checkout I worked in is on `main`, so make sure it lands on the right branch. The new PR run is the real test, because it changes `requirements.txt`.

If it still fails:
- **Another `domain not allowed` line in the post-step:** a further host is blocked.
- **A report about a dependency:** the check is now running properly and has found something in your change.

A v2.21.1 tag of Harden Runner also exists. It isn't needed for this fix, so I didn't change to it.
