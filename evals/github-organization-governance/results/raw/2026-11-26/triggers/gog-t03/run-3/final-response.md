I couldn't read the skill's `policies.md` reference because the permission request was declined. I also have no shell in this session, so I haven't read or changed anything in your organization. Below is the plan I'd follow and the commands to run it. Changing this policy affects every repository in the org, so it needs your approval before anything is applied.

## 1. Read the current state (read-only, needs an org owner token)

```sh
ORG=your-org
gh api orgs/$ORG/actions/permissions                    # enabled_repositories, allowed_actions, sha_pinning_required
gh api orgs/$ORG/actions/permissions/selected-actions   # only meaningful if allowed_actions == "selected"
gh api orgs/$ORG/actions/permissions/workflow           # default GITHUB_TOKEN permissions
gh api enterprises/ENTERPRISE/actions/permissions       # if you have an enterprise: it limits what the org can set
```

Before restricting anything, list the actions your workflows actually use. Otherwise the allowlist will break builds the first time they run:

```sh
set -euo pipefail
work_dir="$(mktemp -d)"
gh api --paginate "orgs/$ORG/repos?per_page=100" --jq '.[] | select(.archived|not) | .full_name' > "$work_dir/repos"
while read -r repo; do
  gh search code --repo "$repo" 'uses:' --extension yml --json path -q '.[].path' 2>/dev/null |
    while read -r path; do
      gh api "repos/$repo/contents/$path" --jq '.content' | base64 -d |
        grep -oE 'uses:\s*[^ #]+' | sed 's/uses:\s*//'
    done
done < "$work_dir/repos" | sed 's/@.*//' | sort | uniq -c | sort -rn > "$work_dir/actions-in-use"
```

This gives you every action owner and name with a usage count. Local `./` actions and reusable workflows show up in the same list.

## 2. Proposed policy (needs your approval before applying)

Store it in a committed file, for example `org-policy/actions-allowlist.json`, so changes can be reviewed and drift can be detected:

```json
{
  "github_owned_allowed": true,
  "verified_allowed": false,
  "patterns_allowed": [
    "your-org/*",
    "docker/login-action@*",
    "aws-actions/configure-aws-credentials@*"
  ]
}
```

To apply it:

```sh
gh api -X PUT orgs/$ORG/actions/permissions \
  -F enabled_repositories=all -f allowed_actions=selected -F sha_pinning_required=true
gh api -X PUT orgs/$ORG/actions/permissions/selected-actions --input org-policy/actions-allowlist.json
gh api -X PUT orgs/$ORG/actions/permissions/workflow \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false
```

Choices I recommend:
- **`verified_allowed: false`.** The Marketplace "verified creator" badge says who published an action, not that its code was reviewed. Allow third-party actions by name only.
- **`sha_pinning_required: true`.** Workflows must then reference actions by full commit SHA. Turning this on will break every workflow that uses a tag like `@v4` until it's re-pinned, so run Dependabot or a pinning tool first. If your API version rejects this field, set it in the org's Settings → Actions page instead.
- **Read-only default `GITHUB_TOKEN`.** Workflows that need write access must then ask for it in their own `permissions:` block.

## 3. Roll it out
1. Pin the actions currently in use to SHAs and fill the allowlist from the inventory in step 1.
2. If you want a softer start, apply the policy to a few repositories first with `enabled_repositories=selected`, then switch to `all`.
3. Watch for failed runs whose message says the action "is not allowed", and either add the action to the allowlist with a recorded reason or replace it.

## 4. Check it worked
- Re-read each setting from step 1 with its own GET request and compare it field by field against `actions-allowlist.json`. The API sometimes accepts a field without applying it.
- Look in the audit log for `org.update_actions_settings` (or a similarly named event) to confirm the change was recorded.
- Create a scratch repository with a workflow that calls an action not on the list, and confirm the run is blocked.
- Check that no repository overrides the org policy. Repositories can only narrow it, but list any that do.

**To go ahead, tell me:**
1. Your org name, and whether there's an enterprise policy above it.
2. Whether to allow verified creators. I recommend no.
3. Whether to require SHA pinning now or after a re-pinning pass.
4. Whether I should run the commands (I'd need shell access), or whether you'd rather run them yourself.
