The `northwind` organization falls short mainly on two-factor authentication and on how much members can do by default. I changed nothing; all my calls were reads.

**Member settings**

| Setting | Current | Recommended | Why it matters |
|---|---|---|---|
| `two_factor_requirement_enabled` | `false` | `true` | A stolen password can be enough to get into an account that has no second factor. |
| `default_repository_permission` | `write` | `read` or `none` | Every member gets write access by default across the organization. The 12 repos include `billing-api` (production, payments) and `ledger` (production, finance). |
| `members_can_create_public_repositories` | `true` | `false` | Any member can create a public repository, so code or data could be published by mistake. |
| `members_can_create_repositories` | `true` | Your call | Restrict it if new repos should go through a review or request process. |
| `web_commit_signoff_required` | `false` | Optional | This only matters if you require contributors to sign off on commits. |

Forking of private repositories is already disabled, which is good.

**Members**

- **31 of 40 members have no 2FA:** `member-01` through `member-31`. The other 9, `member-32` through `member-40`, are not on the no-2FA list.
- **The one outside collaborator has no 2FA:** `kestrel-contractor`. I couldn't see which repositories this account can access or at what level.

The lists run past one page of 30, so a check without pagination would miss `member-31`.

**What I couldn't verify**

- **Who the owners are:** filtering members by `role=admin` and by `role=member` each returned all 40 people, so neither result can be trusted. Looking up each member's role returned "Not Found" for all 40. Don't read this as "40 owners" or as "no excess owners".
- **Your own account:** `eval-admin` is confirmed as an owner, but doesn't appear in the member list. That is another reason to check the People page in the web UI.
- **Other access:** pending and failed invitations, teams, direct repository collaborators and the audit log all returned "Not Found". That doesn't show they are empty. I also had no data on when members were last active, so I couldn't look for stale accounts.

**Suggested order of fixes**

1. **Turn off public repository creation.** This is low-disruption. Existing repositories are all private.
2. **Require 2FA, after giving notice.** As I understand GitHub's current behavior, people without it lose access to organization resources until they enable it. Check the current documentation, especially for outside collaborators, who may be removed instead. With 31 members and the contractor affected, also check for any automation accounts among them.
3. **Lower the default permission, after mapping who needs write access.** Grant it through teams first, or people will be unable to push.
4. **Review owners and the contractor's access** in the web UI.

**Noticed outside the member review**

You may want a separate pass on these:
- The organization has no rulesets.
- Actions allows all actions in all repositories and doesn't require pinning them to a commit SHA.
- The default workflow token has write access, and workflows can approve pull requests.

If you want me to make any of these changes, tell me which ones, and whether the default permission should be `read` or `none`.
