I didn't roll back harden-runner, because the new version isn't what broke the check. I added the blocked host to the allowlist instead. The change is uncommitted and not pushed, so the check on your pull request is still red.

**Cause**

The failed job's post-step in `ci-logs/dependency-review-failed.log` has the line the failing step left out:

```
domain not allowed: api.deps.dev.
```

- **Why it appeared now:** your current pull request changes `requirements.txt`. The last passing run was on a pull request that changed no dependency manifest, and its log shows no lookup of `api.deps.dev` at all.
- **What the action does:** at the pinned v5.0.0, `dependency-review-action` queries `api.deps.dev` when GitHub has no repository URL for a changed package. That request has no error handling, so blocking it fails the step with `fetch failed`.
- **Why the pin looked guilty:** it changed in the same pull request. The passing log never reached this code, so it can't show that v2.20.0 would allow the request. v2.20.0 would get the same allowlist, which doesn't include the host.

**Fix**

One line in `.github/workflows/dependency-review.yml`, under `allowed-endpoints`:

```
api.deps.dev:443
```

This lets the job connect to one more external host, so check you're happy with that. The job stays in `block` mode with `contents: read`. To get the check running, commit and push this to your pull request branch.

**Checks**

- **Pins:** v2.20.0 and v2.21.0 of harden-runner match the SHAs in the passing and failing logs, and the `dependency-review-action` pin matches v5.0.0.
- **`actionlint`:** passed.
- **`zizmor`:** it ran offline and reported two low-severity findings, both for missing `concurrency` settings in `ci.yml` and `dependency-review.yml`. Neither comes from this change, and I left them.
- **Not verified:** the allowlist change is only proven by a run on a pull request that changes a dependency manifest, which yours does. If it still fails, look for another `domain not allowed:` line in the post-step.

**Newer releases**

harden-runner's latest release is v2.23.0, and `dependency-review-action` has v5.0.1. I didn't upgrade either, to keep this fix to one cause, and I didn't check how old those releases are. They're worth a separate pull request.

If you still want v2.20.0 for another reason, its SHA is `bf7454d06d71f1098171f2acdf0cd4708d7b5920`. `ci.yml` uses the same harden-runner pin, so change both or they'll differ. You'd still need the `api.deps.dev` line.
