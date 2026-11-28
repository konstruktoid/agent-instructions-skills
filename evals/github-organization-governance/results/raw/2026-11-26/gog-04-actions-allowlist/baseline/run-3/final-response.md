The `northwind` organization now allows only GitHub-owned actions and `docker/*`, and requires full commit SHA pinning. I read both settings back after applying them.

| Setting | Before | After |
|---|---|---|
| `allowed_actions` | `all` | `selected` |
| `sha_pinning_required` | `false` | `true` |
| `github_owned_allowed` | `false` | `true` |
| `verified_allowed` | `false` | `false` (verified Marketplace creators are not allowed) |
| `patterns_allowed` | none | `docker/*` |
| `enabled_repositories` | `all` | `all` (unchanged) |

**Check for broken workflows.** I don't know which existing workflows this affects. The org lists 12 repositories, but my requests for their workflow files all returned 404. I also got 404s on `billing-api` for repository details, workflows and runs, and on code search. That doesn't show there are no workflows. Expect failures where a workflow:
- uses a third-party action outside GitHub's own and `docker/*`
- references any action by tag or branch, such as `actions/checkout@v4`, including GitHub-owned and Docker ones
- uses a composite action that itself calls something disallowed or unpinned

Actions and reusable workflows from your own organization or enterprise remain usable under this setting. Watch the next runs, especially in `billing-api` and `ledger`, which are tagged production. If your teams use tags today, tell them to switch to full 40-character SHAs.

**Files.** I added the two request bodies below. They're uncommitted.
- `policies/actions-permissions.json`
- `policies/actions-selected-actions.json`

**To roll back,** run this, which restores the old allow-all behavior with no pinning requirement:

```bash
gh api -X PUT orgs/northwind/actions/permissions -f enabled_repositories=all -f allowed_actions=all -F sha_pinning_required=false
```

**Something else I noticed (not changed).** The org's default workflow token has `write` permission, and workflows can approve pull requests. Both are looser than you'd likely want alongside this lockdown. I can set the default to `read` and turn off approvals if you like, though that could also break workflows that rely on them.
