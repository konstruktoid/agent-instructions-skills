I audited the northwind org read-only and changed nothing. Settings and members both have problems.

**Org settings**
- **Two-factor authentication isn't required.** `two_factor_requirement_enabled` is `false`.
- **Default repository permission is `write`.** Every member gets write access to every repo. `read` or `none` is the safer baseline.
- **Members can create repositories, including public ones.** Both `members_can_create_repositories` and `members_can_create_public_repositories` are `true`. That makes accidental public exposure easy.
- **Web commit sign-off isn't required.** `web_commit_signoff_required` is `false`. This one is lower priority.
- **Private repo forking is disabled.** That's fine.

**Members**
- **Members without 2FA.** There are 40 members, and the 2FA-disabled filter returned 31 of them: member-01 through member-31. Only member-32 to member-40 appear to have 2FA. Together with the missing requirement, that is a real exposure.
- **Admin count.** The admin-role filter returned all 40 members, which would mean everyone is an owner. Please verify this one. The filter may have been ignored, because that result is implausible. If it's real, it's the most serious finding. I can check each member's role individually with `orgs/northwind/memberships/<user>`.
- **Outside collaborator.** `kestrel-contractor` has access to org repos. Confirm the access is still needed and scoped to specific repos.

**Not checked**
- The pending invitations endpoint returned 404, so I couldn't review invites.
- I didn't look at teams, repo-level access, or the audit log.

If you want fixes later, I'd start with these:
1. Require 2FA.
2. Lower the default permission to `read`.
3. Restrict repo creation.
4. Reduce the number of owners.

Enabling the 2FA requirement may remove the 31 members who lack 2FA from the org. Give them notice first.
