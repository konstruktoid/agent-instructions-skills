I added `api.deps.dev:443` to the egress allowlist in `.github/workflows/dependency-review.yml` and did not roll back the harden-runner pin. I haven't run the workflow, and I haven't committed or pushed anything.

**Why I didn't roll back:** the failed log shows harden-runner v2.21.0 working as configured. The post-step reports `domain not allowed: api.deps.dev.`, so the egress policy blocked that request.

**Why the check failed now:** the Dependency Review action queries `api.deps.dev` when a PR changes a manifest. This PR changes `requirements.txt`. The last passing run was a PR that changed no manifest, so it never made that call. The bare "fetch failed" is Node's error for a blocked connection. A v2.20.0 pin would block `api.deps.dev` the same way.

**To confirm:** push the change and re-run the check on this PR. If it still fails, the post-step "domain not allowed" lines will name any other endpoint that needs allowing.

If you still want the pin back at v2.20.0 for some other reason, tell me. The passing log shows `bf7454d0…`, which I take to be v2.20.0, but I haven't verified that.
