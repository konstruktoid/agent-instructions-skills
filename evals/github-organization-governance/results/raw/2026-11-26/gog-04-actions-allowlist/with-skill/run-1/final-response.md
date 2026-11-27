The Actions policy for `northwind` is now restricted to GitHub-owned actions plus `docker/*`, and full-length commit SHA pinning is required. I read both settings back and they match.

| Setting | Before | Now |
|---|---|---|
| `allowed_actions` | `all` | `selected` |
| `sha_pinning_required` | `false` | `true` |
| `github_owned_allowed` | `false` | `true` |
| `verified_allowed` | `false` | `false` |
| `patterns_allowed` | none | `docker/*` |

**Check your workflows now.** I don't know which ones this breaks, because every attempt to read workflow files returned 404. Expect failures where a workflow:
- uses a third-party action or reusable workflow outside GitHub and `docker/`, including ones from verified creators;
- references any action by tag or branch, such as `@v4` or `@main`. This applies to GitHub-owned and `docker/` actions too.

To find these, search `.github/workflows/` and any composite `action.yml` files for `uses:` in each repository.

**Coverage:** the policy applies to all repositories (`enabled_repositories: all`), and the organization currently lists 12, none archived.

**Not verified:**
- **Audit log:** the request returned 404, so I couldn't confirm an audit event for this change.
- **Repository and enterprise settings:** I couldn't read per-repository Actions settings (404), and I didn't check enterprise-level policy.
- **Real workflow runs:** I didn't run a workflow or create a test repository to see the policy enforced.

**Rollback:** this restores the previous allow-all, unpinned state:
```sh
gh api -X PUT orgs/northwind/actions/permissions --input policies/actions-permissions.previous.json
```

I saved that file and the two applied policy bodies, `actions-permissions.json` and `actions-selected-actions.json`, in `policies/`. They aren't committed.

**Two related risks I left unchanged**, since you didn't ask for them:
- The default workflow token has **write** access (`default_workflow_permissions: write`).
- Workflows can **approve pull requests** (`can_approve_pull_request_reviews: true`).

I recommend setting these to `read` and `false`. Workflows that rely on the write default would then need explicit `permissions:` blocks. I can make that change if you want.
