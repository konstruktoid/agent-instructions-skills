I added `api.deps.dev:443` to the egress allowlist in `.github/workflows/dependency-review.yml`. I haven't committed or pushed it, and I couldn't run the check from here, so it isn't confirmed green yet. Push it and the check will re-run on the PR.

- **Cause:** the failed log's post-step says `domain not allowed: api.deps.dev.`. Your PR changes `requirements.txt`, so the dependency review action looks up the new packages on `api.deps.dev`. harden-runner is in `block` mode and that host wasn't allowed, so the request was dropped and Node printed `fetch failed`.
- **Why it passed before:** the last passing run changed no dependency manifest, so it never made that call.
- **Why I didn't roll back the pin:** the old version would block `api.deps.dev` in the same way, so the rollback wouldn't have fixed the check. The pin change is a coincidence.
- **Pin left at v2.21.0:** I also left `ci.yml` alone.

The `api.deps.dev` entry widens your egress policy by one host. It's the endpoint the action needs for manifest changes, but check that you're comfortable allowing it.
