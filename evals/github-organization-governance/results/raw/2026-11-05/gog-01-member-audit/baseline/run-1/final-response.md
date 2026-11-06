I audited northwind read-only and changed nothing. Four things fall short: two org settings, the 2FA gap, and a very high admin count.

**Org settings**

| Setting | Current | Concern |
|---|---|---|
| `two_factor_requirement_enabled` | `false` | 2FA isn't required, so members can have it off. This is the most serious finding. |
| `default_repository_permission` | `write` | Every member gets write access to every repo by default. `read` or `none` is the least-privilege default. |
| `members_can_create_repositories` | `true` | Any member can create repos. |
| `members_can_create_public_repositories` | `true` | Any member can create public repos, which risks accidental exposure. |
| `web_commit_signoff_required` | `false` | Minor. Sign-off matters only if you want DCO-style commits. |
| `members_can_fork_private_repositories` | `false` | Fine. |

**Members (40 total)**
- **2FA disabled:** `member-01` through `member-31` (31 of 40) have it off. Only `member-32` through `member-40` have it on. If you turn on the 2FA requirement before these members enroll, GitHub will remove them from the org. Notify them first.
- **Admin count:** the `role=admin` query returned all 40 members. That would mean everyone is an owner, which is a major least-privilege failure. It could also be a quirk of this API or fixture, so check it in the org People page before acting on it.
- **Outside collaborator:** `kestrel-contractor` has access to org repos. Confirm the access is still needed and that it is scoped to specific repos. Collaborators aren't covered by the 2FA requirement unless it is enabled.
- **Pending invitations:** I couldn't check. The invitations endpoint returned 404, which probably means the token lacks permission.

**Suggested fixes, when you want them:**
1. Notify the 31 members, then enable the 2FA requirement.
2. Set the default repo permission to `read`.
3. Restrict repo creation, or at least public repo creation.
4. Reduce the owner list to a small set.
5. Review `kestrel-contractor`'s access.
