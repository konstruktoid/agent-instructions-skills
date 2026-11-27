`northwind` now allows only GitHub-owned actions and `docker/*`, and requires actions to be pinned to a full commit SHA. I read both settings back after applying them.

| Setting | Before | After |
|---|---|---|
| `allowed_actions` | `all` | `selected` |
| `sha_pinning_required` | `false` | `true` |
| `github_owned_allowed` | `false` (not in effect while all actions were allowed) | `true` |
| `verified_allowed` | `false` | `false` |
| `patterns_allowed` | none | `docker/*` |

`enabled_repositories` is still `all`.

**Check your workflows now.** I couldn't find out what your workflows currently use: workflow listings and code search returned 404. That doesn't show there are no workflows. Expect failures where a workflow, including through a composite action or reusable workflow it calls, does either of these:
- uses a third-party action outside GitHub's own and `docker/`, including Marketplace "verified creator" ones;
- references any action by tag or branch, such as `actions/checkout@v4`. The pinning rule applies to GitHub-owned and `docker/` actions too.

To roll back both restrictions:

```sh
gh api -X PUT orgs/northwind/actions/permissions \
  -f enabled_repositories=all -f allowed_actions=all -F sha_pinning_required=false
```

**Not verified**
- **Audit evidence:** the audit log request returned 404, so I couldn't confirm the change was recorded. Check it in the organization's audit log settings page.
- **Coverage:** the policy is set organization-wide, but the per-repository permission reads for all 12 repositories also returned 404. I haven't confirmed it in any individual repository or tested it with a workflow run.
- **Enterprise policy:** the organization is on an enterprise plan, and I didn't check the enterprise-level Actions settings.

**Files:** the applied settings are saved in `policies/actions-permissions.json` and `policies/actions-selected-actions.json`. They're uncommitted.

**Related risk, left unchanged:** the default workflow token is still `write`, and workflows can approve pull requests (`can_approve_pull_request_reviews: true`). So an allowed action can still get write access by default. I recommend changing these to `read` and `false`. It could break workflows that rely on the defaults, so I'd want your approval first.
