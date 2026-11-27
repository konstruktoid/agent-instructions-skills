I can't change your organization from here. This session has no shell, so I can't run `gh api` against GitHub, and the request to read the skill's `references/policies.md` was declined. Nothing has been read or changed yet. Below is the procedure to run yourself, or I can run it if you grant shell access and tell me the organization name.

## 1. Read the current state first

```sh
ORG=your-org
gh api orgs/$ORG/actions/permissions                     # enabled_repositories, allowed_actions
gh api orgs/$ORG/actions/permissions/selected-actions    # current allowlist, if allowed_actions=selected
gh api orgs/$ORG/actions/permissions/workflow            # default GITHUB_TOKEN permissions
gh api orgs/$ORG/actions/permissions/repositories --paginate   # only if enabled_repositories=selected
```

If you're on GitHub Enterprise, check the enterprise actions policy too. The organization can only be stricter than it, never looser.

## 2. Build the allowlist from what you actually use

If you lock this down without checking usage, workflows that call actions not on the list will fail. List every `uses:` reference across the organization first:

```sh
set -euo pipefail
work_dir="$(mktemp -d)"
gh api --paginate "orgs/$ORG/repos?per_page=100" --jq '.[] | select(.archived==false) | .name' \
  | sort > "$work_dir/repos"
while read -r repo; do
  gh search code --owner "$ORG" --repo "$ORG/$repo" 'uses:' --filename '*.yml' --json path,textMatches \
    --jq '.[].textMatches[].fragment' 2>/dev/null || echo "SEARCH-FAILED $repo" >&2
done < "$work_dir/repos" | grep -oE 'uses:\s*[^ @]+' | sort | uniq -c | sort -rn
```

Code search has rate limits and can miss files. Treat this list as a starting point, and back it up with the violations step in section 4.

## 3. Proposed policy (needs your approval before I apply anything)

These changes affect every repository in the organization, so I'd want your explicit go-ahead first.

```sh
# Allow only selected actions
gh api -X PUT orgs/$ORG/actions/permissions \
  -f enabled_repositories=all -f allowed_actions=selected

# Allowlist: GitHub-owned and verified creators are optional; explicit entries pinned by owner/repo
gh api -X PUT orgs/$ORG/actions/permissions/selected-actions --input - <<'JSON'
{
  "github_owned_allowed": true,
  "verified_allowed": false,
  "patterns_allowed": [
    "docker/login-action@*",
    "your-org/*"
  ]
}
JSON

# Make the default workflow token read-only, and stop workflows from approving PRs
gh api -X PUT orgs/$ORG/actions/permissions/workflow \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false
```

What I'd recommend:
- **Set `verified_allowed` to `false`.** "Verified creator" says who published an action, not that it's safe to run.
- **Make each entry in `patterns_allowed` a specific `owner/repo`.** Avoid broad wildcards. If your policy requires full commit SHA pinning, turn on GitHub's "require actions to be pinned to a full-length commit SHA" setting where your plan offers it. Note that a SHA pin can still point at an imposter commit from a fork. Pinning stops a tag from being moved, but it doesn't prove where the commit came from.
- **Record every exception in a committed policy file** with a reason, an owner and an expiry, so it can be reviewed and checked for drift.

## 4. Verify after applying

1. **Read each setting back** with a separate request (the three GET calls from section 1). Compare them field by field with what you meant to set. An accepted PUT doesn't prove the setting took effect.
2. **Measure coverage.** If `enabled_repositories=selected`, list the repositories that are excluded, by name.
3. **Check for broken workflows.** Look for runs that failed with "action is not allowed" over the next few days, then add the missing actions to the allowlist or fix those workflows.
4. **Confirm the audit log event.** Look for `org.update_actions_settings` or a similar entry, so the change has evidence behind it.
5. **Test with a new repository.** Create a scratch repository and confirm a workflow calling an action that isn't on the list is blocked, without configuring that repository by hand.

**Next step:** tell me the organization name and whether you're on Enterprise. If you allow shell access, I'll run the reads in sections 1 and 2 and draft the exact allowlist from your actual usage before proposing any change.
