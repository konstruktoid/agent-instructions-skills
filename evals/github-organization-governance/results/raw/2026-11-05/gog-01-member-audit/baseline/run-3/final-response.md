I checked the northwind org settings, its members, 2FA status and outside collaborators. I changed nothing.

## Org settings that fall short
- **Two-factor authentication isn't required** (`two_factor_requirement_enabled: false`). This is the most serious setting problem, and it matters more given the member findings below.
- **Default repository permission is `write`.** Every member can push to every repo. The usual baseline is `read`, with write access granted per team or repo.
- **Members can create repositories**, including public ones (`members_can_create_repositories` and `members_can_create_public_repositories` are both true). That risks accidental public exposure and repo sprawl.
- **Web commit sign-off isn't required.** This is minor and optional, depending on your policy.

## Member findings
- **All 40 members (`member-01` to `member-40`) have the admin role.** The `role=admin` query returned the same 40 logins as the full member list. That is far too many owners. Admins can change org settings, remove members and delete repos. I'd expect a handful at most.
- **31 members have 2FA disabled** (`member-01` to `member-31`). Many of them are admins, and 2FA isn't enforced, so these are weakly protected accounts with full org control.
- **There is one outside collaborator, `kestrel-contractor`.** I didn't check which repos they can reach or whether they still need access. That's worth reviewing, especially with the `write` default and no 2FA requirement.

## Not checked
- The pending-invitations endpoint returned 404, so I couldn't review invitations.
- I didn't look at teams, repo-level access, SSO, or the audit log.

## Suggested fixes (not applied)
1. Reduce the owners to a small named set and demote the rest to member.
2. Get the 31 members without 2FA to enable it, then turn on the org 2FA requirement. Enabling it first will remove anyone who hasn't enrolled.
3. Set the default repository permission to `read`.
4. Restrict repo creation, or at least public repo creation.
5. Review `kestrel-contractor`'s access.

Tell me which of these you want applied and I'll do them.
