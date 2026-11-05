The northwind actions policy is applied and verified by a separate read-back of each setting:

- **Allowed actions:** `selected`.
- **GitHub-owned actions:** allowed.
- **Pattern allowlist:** `docker/*`.
- **Verified-partner actions:** not allowed.
- **SHA pinning:** required (`sha_pinning_required: true`).

I saved the request bodies as `policies/actions-permissions.json` and `policies/selected-actions.json`, so the policy can be diffed and reapplied. I haven't committed them.

**Not checked:**
- **Fleet coverage:** this is an organization-level setting, so it applies to every repository with `enabled_repositories: all`. I didn't measure per-repository effects.
- **Existing workflows:** I didn't scan them for unpinned or non-allowlisted actions. Workflows that use tag references or other third-party actions will start failing.
- **Audit event:** I didn't confirm that an audit log entry was written.

**Still open:** the default workflow token is `write`, and workflows can approve pull request reviews. The baseline calls for a read-only token. You didn't ask for that change, so I left it alone. If you want it, I can set `default_workflow_permissions` to `read` and `can_approve_pull_request_reviews` to `false`.
