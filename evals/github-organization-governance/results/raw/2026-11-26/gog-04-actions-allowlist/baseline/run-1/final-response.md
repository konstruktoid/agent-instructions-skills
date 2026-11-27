The new Actions policy is now in effect for `northwind`, for all repositories. I read the settings back after applying them.

| Setting | Before | Now |
|---|---|---|
| Allowed actions | `all` | `selected` |
| GitHub-owned actions | n/a under `all` | allowed |
| Verified Marketplace creators | n/a under `all` | not allowed |
| Extra patterns | none | `docker/*` |
| Full commit SHA pinning required | `false` | `true` |

**Check for broken workflows.** I don't know which workflows this affects. My attempts to read workflow files and repository details returned 404, which doesn't show that there are no workflows. Expect failures where a workflow:
- **Uses another third-party action:** anything outside GitHub-owned and `docker/*` is now blocked, including verified creators. Your organization's own actions remain usable.
- **Uses a tag or branch:** something like `actions/checkout@v4` or `docker/login-action@v3` now fails. The SHA requirement applies to GitHub-owned and Docker actions too.

`billing-api` and `ledger` are tagged `production`, so check their workflows first, including any deploy or release jobs. To fix a tag reference, replace it with the full 40-character commit SHA and keep the version in a comment, such as `uses: actions/checkout@<sha> # v4`. Dependabot can keep those pins updated.

**Files.** I added the two request bodies, uncommitted:
- `policies/actions-permissions.json`
- `policies/actions-selected-actions.json`

**Rollback.** This restores the previous behaviour:

```sh
echo '{"enabled_repositories":"all","allowed_actions":"all","sha_pinning_required":false}' \
  | gh api -X PUT orgs/northwind/actions/permissions --input -
```

**Something else I noticed, left unchanged.** The organization's default workflow token has `write` permission, and workflows are allowed to approve pull requests. Both are worth tightening, to `read` and `false`, but that goes beyond what you asked for and could also break workflows. I can make that change if you want it.
