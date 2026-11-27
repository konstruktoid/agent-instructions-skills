I haven't changed anything yet. I can't run `gh` in this session, and I wasn't allowed to read the skill's `references/policies.md`, so the steps below come from the skill's baseline and GitHub's REST API. Changing the actions policy affects every repository in the organization, so check the current state first and approve each write separately.

## 1. Read the current state (replace `ORG` with your organization name)

```sh
gh api orgs/ORG/actions/permissions
gh api orgs/ORG/actions/permissions/selected-actions   # only meaningful if allowed_actions == "selected"
gh api orgs/ORG/actions/permissions/workflow
gh api enterprises/ENTERPRISE/actions/permissions      # if you're on Enterprise; it limits what the org can set
```

Also list which actions your workflows actually call today, so the allowlist doesn't break them:

```sh
gh search code --owner ORG 'uses:' --filename '*.yml' --json repository,path --limit 1000
```

## 2. Apply the restriction (needs an organization owner token)

Policy file to commit for review (e.g. `org-policy/actions-allowlist.json`):

```json
{
  "github_owned_allowed": true,
  "verified_allowed": false,
  "patterns_allowed": [
    "ORG/*",
    "docker/login-action@*",
    "aquasecurity/trivy-action@*"
  ]
}
```

Replace the example third-party patterns with the ones your step 1 inventory found. Prefer listing named actions over `verified_allowed: true`, which allows every verified creator.

```sh
# Allow selected actions only (for all repos; or use "selected" repos plus an explicit list)
gh api -X PUT orgs/ORG/actions/permissions \
  -f enabled_repositories=all -f allowed_actions=selected

# Set the allowlist from the committed file
gh api -X PUT orgs/ORG/actions/permissions/selected-actions \
  --input org-policy/actions-allowlist.json

# Make the default workflow token read-only, and stop workflows from approving PRs
gh api -X PUT orgs/ORG/actions/permissions/workflow \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false
```

If your plan supports it, also require full-length commit SHA pinning. This is the `sha_pinning_required` field on `orgs/ORG/actions/permissions`. Check the current REST docs for the exact field name before you rely on it.

## 3. Verify

- **Read each setting back** with the three GET calls from step 1. Compare them field by field with the file, because the API can accept a field without applying it.
- **Check coverage across the organization.** Repositories can only narrow the org policy, not widen it. Check that none has Actions disabled for an unintended reason, or a stricter list that leaves it with no allowed actions:
  ```sh
  set -euo pipefail
  gh api --paginate "orgs/ORG/repos?per_page=100" --jq '.[] | select(.archived|not) | .full_name' |
    while read -r r; do printf '%s ' "$r"; gh api "repos/$r/actions/permissions" --jq '.allowed_actions // "disabled"'; done
  ```
- **Check the audit log.** It should contain an `org.update_actions_settings` (or similar) event for each change.
- **Check what breaks.** Run a workflow that uses an action not on the list. It should fail with "action is not allowed". Also run a few real CI pipelines to confirm they still pass.
- **Record the control.** Write down the mechanism (the committed file), the evidence (the read-back output and the audit event) and the owner. Any action allowed only as an exception needs a reason and an expiry.

## Before anything is applied, I need from you:
1. The organization name, and whether there's an enterprise policy above it.
2. Which third-party actions you need to allow, or permission to build the list from the step 1 inventory.
3. Explicit approval for the three `PUT` calls. Switching to `selected` will immediately fail any workflow that calls an action not on the list.

If you run the step 1 reads and paste the output, I'll draft the exact allowlist file.
