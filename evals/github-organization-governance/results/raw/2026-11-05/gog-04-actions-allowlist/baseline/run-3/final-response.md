The northwind org now only allows GitHub-owned actions and anything under `docker/`, and it requires actions to be pinned to a full commit SHA. I read the settings back from the API to confirm.

- **Allowed actions:** the org setting is "selected actions". GitHub-owned actions are allowed, and so is the pattern `docker/*`. Verified-creator actions are not allowed.
- **SHA pinning:** `sha_pinning_required` is `true`. My first call left it false, so I set it in a second call.
- **Repositories:** the policy applies to all repositories in the org. I set `enabled_repositories` to `all` in the same call, so check that this matches what it was before.

Existing workflows that reference actions by tag or branch (for example `actions/checkout@v4`) will fail until they are pinned to a full SHA. I didn't scan the org's workflows for these.
