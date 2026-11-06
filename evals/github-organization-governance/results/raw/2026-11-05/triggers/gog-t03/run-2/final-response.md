I can't proceed yet, and I haven't changed anything. Two things are in the way:

1. **I couldn't read the skill's policy reference.** The read of `references/policies.md` was denied. It holds the detail for allowed-actions policy, so I don't want to apply it from memory. If you grant read access to that path, I'll continue.
2. **I need a few details from you.** I also have no `gh` or shell access in this session, so I can't read or write org settings yet.
   - **Org name:** which organization is this?
   - **Allowlist:** which of these do you want?
     - GitHub-owned actions only.
     - GitHub-owned actions plus verified creators.
     - A specific list of patterns, such as `owner/repo@sha` entries. Please send the list.
   - **Credentials:** an org-owner `gh` token, with the `admin:org` scope, is needed for these endpoints.

**Planned change.** This is the sequence once access is sorted:
1. Read the current state with `gh api orgs/ORG/actions/permissions` and `.../permissions/workflow`.
2. Set `allowed_actions` to `selected` and apply the allowlist through `.../actions/permissions/selected-actions`. I'd keep the allowlist in a committed file so it can be reviewed and re-applied.
3. Set the default workflow token to read-only.
4. Read each setting back with a separate request and compare it to the intent.
5. Check for enterprise-level policy that would override the org setting.

Restricting actions can break workflows in existing repositories that use actions outside the list. I'll show you the exact change and get your approval before applying it. I'll also scan the repositories' workflows for actions the list would block.
