I found problems in both the member settings and the members. The most urgent are that **31 of 40 members have no two-factor authentication (2FA)** and that every member gets write access by default. I changed nothing; all calls were reads.

## Member settings

| Setting | Current | Should be | Why it matters |
|---|---|---|---|
| `two_factor_requirement_enabled` | `false` | `true` | A stolen password can be enough to get into an account. |
| `default_repository_permission` | `write` | `read` or `none` | Members can push to all 12 repositories unless something at repository level stops them. There are no organization rulesets. |
| `members_can_create_public_repositories` | `true` | `false` | Any member can publish a new public repository. |
| `members_can_create_repositories` | `true` | Your call | A new repository isn't required to be classified, since the `tier` property is optional. |

Forking of private repositories is already disabled, which meets the baseline.

## Members

**31 members without 2FA:** `member-01` through `member-31`, all of them in that range. The other nine, `member-32` through `member-40`, are not on the list. This needed all pages of results, as the first page stops at 30.

**One outside collaborator:** `kestrel-contractor`. I couldn't find which repositories they can access (the per-repository lookups returned 404), their 2FA status, or an owner or expiry date for the access.

## What I couldn't check
These are unknowns, not passes:

- **Who the owners are:** filtering members by `role=admin` returned all 40, but so did `role=member`. The filter isn't separating roles, so don't read this as 40 owners. Check the People page in the web interface.
- **Visibility changes, deletion, transfer and outside-collaborator invitations:** the organization response didn't include these settings.
- **Teams and direct access grants:** the teams lookup returned 404, so I can't tell who would lose access if the default permission were lowered.
- **Tokens and audit log:** the token, token-request and audit log lookups returned 404.
- **Single sign-on, automated provisioning and enterprise policy:** I didn't read these. The organization is on the enterprise plan, so check whether enterprise policy limits any of the settings above.

## Related problems outside member settings
I came across these while reading the organization:

- **Actions:** all actions are allowed and pinning to a commit SHA isn't required.
- **Workflow token:** it defaults to `write`, and workflows can approve pull requests.
- **Runners:** the `Default` runner group is visible to all repositories. All 12 are private today, but I didn't check whether the group admits public ones or has any runners.
- **Classification:** `billing-api` and `ledger` have no `tier` value, although both are tagged `production`. A ruleset targeting `tier=production` would miss them.

## Suggested order, once you approve
1. **2FA:** tell the 31 members and `kestrel-contractor` to enroll by a set date, then require it. Enforcing it can cut off or remove accounts that haven't enrolled, so check GitHub's current behavior first. Check any automation accounts too.
2. **Public repositories:** stop members creating them. This is a small change that's easy to reverse.
3. **Default permission:** work out who relies on the implicit write access, grant it through teams, then lower the default to `read`.
4. **Owners and contractor:** confirm the owner list, and give the contractor's access an owner and an expiry date, or remove it.

Tell me which of these you want to go ahead with. Each change would need your approval before I apply it.
