I can't proceed with the change yet. Reading the skill's policy reference (`references/policies.md`) was denied, and that file covers the allowed-actions policy.

Applying the change would also need three things I don't have:

- **Which organization.** You didn't name one, and the working directory isn't tied to an organization I can identify.
- **What "restrict" means.** The options are `selected` (an allowlist) or `local_only` (only actions from the organization's own repositories). If you pick `selected`, I need to know whether to allow GitHub-authored actions, Marketplace verified creators, or specific `owner/repo@sha` patterns.
- **Your approval to write.** Changing organization-wide Actions policy affects every repository, so I'll confirm the exact settings with you before applying anything.

Once you've told me the organization and the policy, I'll do this:
1. Read the current state with `gh api orgs/ORG/actions/permissions` and `.../actions/permissions/workflow`.
2. Apply the allowlist, and set the default workflow token to read-only.
3. Read each setting back through a separate request to confirm it applied.
4. Report which repositories the policy reaches, with any misses listed by name.

If you'd like me to continue, please grant read access to the skill's reference folder. Otherwise I'll work from the baseline in the skill itself.
