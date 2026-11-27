I found three clear failures in the member settings, and most members have no two-factor authentication (2FA). I only read data; nothing was changed.

## Member settings

| Setting | Now | Should be | Why it matters |
|---|---|---|---|
| `two_factor_requirement_enabled` | `false` | `true` | A stolen password can be enough to take over an account. |
| `default_repository_permission` | `write` | `read` or `none` | Every member can push to all repositories, and I found no organization rulesets limiting that. |
| `members_can_create_public_repositories` | `true` | `false` | Any member, or anyone holding a member's account, can publish a public repository. |

- **Worth a decision:** `members_can_create_repositories` is `true`. Restricting it is optional, but with no required custom properties, new repositories can go unclassified.
- **Meets the baseline:** members cannot fork private repositories.

## Members
**31 of 40 members have 2FA disabled:** `member-01` through `member-31`. Only `member-32` through `member-40` are not on that list.

**The one outside collaborator, `kestrel-contractor`, also has 2FA disabled.** I couldn't see which repositories they can access or at what level, and found no owner or expiry date for that access.

## What I couldn't check
This is a partial audit, so none of these should be read as passing:

- **Who the owners are:** filtering members by `role=admin` and by `role=member` both returned all 40, so the filter isn't working. I can't say that all 40 are owners, or whether any owner lacks 2FA. Check the People page in GitHub.
- **Teams and repository grants:** the team list, and each repository's teams and collaborators, returned 404.
- **Visibility changes, deletion and transfer:** the organization response had no fields showing whether members can do these.
- **Single sign-on and automated provisioning:** I read nothing that shows either one.
- **Tokens, audit log and invitations:** the token, token request, credential authorization, audit log and pending or failed invitation reads returned 404.

A 404 doesn't tell me whether the data is missing, the credential lacks access or the endpoint is unavailable.

## Noticed outside the member scope
- **Actions:** all actions are allowed, SHA pinning isn't required, and the default workflow token has `write` and can approve pull requests.
- **Runners:** the `Default` runner group is visible to all repositories. All 12 repositories are currently private.
- **Rulesets:** the organization has none.
- **Classification:** `billing-api` and `ledger` have no `tier` property, although their topics include `production`. A ruleset targeting `tier=production` would miss both.

## Suggested order, each needing your approval
1. **Turn off public repository creation.** This is a small change that closes an immediate exposure.
2. **Move to required 2FA.** Give the 31 members and `kestrel-contractor` a deadline first. Enforcement can cut off their access or remove them, so check GitHub's current behavior and make sure at least one owner has 2FA and recovery codes.
3. **Lower the base permission.** First find who relies on the implicit `write` access and grant it through teams, or their pushes will start failing. This needs the team and access data I couldn't read.

To finish the audit, I need the owner list, team and repository access, and the single sign-on status, for example from the GitHub settings pages or an export.
