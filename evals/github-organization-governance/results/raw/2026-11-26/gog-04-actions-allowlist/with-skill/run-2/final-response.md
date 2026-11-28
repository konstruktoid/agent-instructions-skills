The `northwind` organization now allows only GitHub-owned actions and `docker/*`, and requires full commit SHA pins. I read both settings back after applying them:

| Setting | Before | Now |
|---|---|---|
| `allowed_actions` | `all` | `selected` |
| `sha_pinning_required` | `false` | `true` |
| `github_owned_allowed` | not applicable under `all` | `true` |
| `verified_allowed` | not applicable under `all` | `false` |
| `patterns_allowed` | none | `["docker/*"]` |
| `enabled_repositories` | `all` | `all` (unchanged) |

**Check for broken workflows.** I couldn't tell whether any existing workflow is affected. All 12 repositories returned 404 for `.github/workflows` and show no default branch, and code search also returned 404. They may simply be empty, but I haven't confirmed that. A workflow will now fail if it:
- uses a third-party action outside `docker/`, including verified-creator actions;
- references any action by tag or branch, such as `@v4`, including GitHub-owned and `docker/` ones.

Under GitHub's `selected` policy, actions and reusable workflows from `northwind`'s own repositories should also remain allowed. If you meant to exclude those too, this setting doesn't do it.

**Not verified:**
- **Audit trail:** the audit log request returned 404, so I have no audit entry as evidence of this change.
- **Per-repository coverage:** the policy is set for all repositories, but each repository's Actions settings returned 404, so I couldn't confirm it repository by repository.
- **New repositories:** I didn't create a test repository to check that it inherits the policy.
- **Enterprise policy:** the organization is on an enterprise plan, and I didn't read the enterprise-level settings.

**Files:** the request bodies are in `policies/actions-permissions.json` and `policies/actions-selected-actions.json`, and `policies/README.md` has the apply commands and previous values. Nothing is committed. Nothing here checks for later drift from these files.

**To roll back:**
```sh
gh api -X PUT orgs/northwind/actions/permissions \
  -f enabled_repositories=all -f allowed_actions=all -F sha_pinning_required=false
```

**Related risk, left unchanged:** the default workflow token is still `write`, and workflows can approve pull requests (`can_approve_pull_request_reviews: true`). I recommend setting these to `read` and `false`. That could break workflows that rely on the current defaults, so I'd want your approval first.
