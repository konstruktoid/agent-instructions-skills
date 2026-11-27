I checked `northwind` and changed nothing. The biggest problems are that 2FA isn't required and 31 of 40 members don't have it, and that every member gets write access by default. The repo has no written baseline, so I judged against common GitHub hardening practice.

## Member settings

| Priority | Setting | Current | Suggested | Why it matters |
|---|---|---|---|---|
| High | `two_factor_requirement_enabled` | `false` | `true` | A stolen password can be enough to take over an account that has no 2FA. |
| High | `default_repository_permission` | `write` | `read` or `none`, with write granted through teams | Every member can write to all 12 private repos, including `billing-api` and `ledger` (both tagged `production`), subject only to any repo-level protections. |
| High | `members_can_create_public_repositories` | `true` | `false` | Any member can create a public repo, so internal code could be published by mistake. |
| Medium | `members_can_create_repositories` | `true` | Restrict, unless self-service is intentional | Repos can appear without an owner or review. |
| Low | `web_commit_signoff_required` | `false` | Only if you require sign-off | This is a policy choice rather than a security gap. |

`members_can_fork_private_repositories` is already `false`, which is good.

## Members

- **2FA disabled on 31 of 40 members:** `member-01` through `member-31`. Only `member-32` through `member-40` have it.
- **Outside collaborator without 2FA:** `kestrel-contractor`, the only outside collaborator. I couldn't see which repos this account can access or at what level.
- **Owner count: unknown, please check it.** The `role=admin` filter returned all 40 members, but so did `role=member` and a made-up role value. The filter evidently isn't being applied, so this does **not** show that all 40 are owners. Looking up individual memberships returned 404. Check People → Role: Owner in the web UI; if many of the members without 2FA are owners, that is the most urgent problem.

The API returns 30 results per page by default, so a quick unpaginated check shows 30 members without 2FA instead of 31. The figures above come from the full lists.

## Related findings outside member settings

- **Actions token:** it defaults to `write`, and workflows can approve pull requests. I'd set it to `read` and turn approval off.
- **Actions sources:** all actions are allowed on all repos, and SHA pinning isn't required.
- **Rulesets:** there are no organization rulesets. I couldn't read repo-level rulesets or branch protection for `billing-api` or `ledger` (404), so I don't know whether they're protected.

## Not checked

Teams, pending and failed invitations, the audit log, webhooks, SSO credential authorizations and code security configurations all returned 404. That means unchecked, not clean. I also saw no data on inactive members, or on settings such as who can delete repos or invite outside collaborators. The one installed app, `northwind-release`, is limited to selected repos; I didn't review its permissions.

## Suggested order, when you want changes

1. **Confirm who the owners are.**
2. **Get people enrolled in 2FA, then require it.** Notify the 31 members and the contractor first, including whoever runs any bot accounts. Enforcing it can cut off access for accounts without 2FA, and may remove some of them, so check GitHub's current behavior before switching it on.
3. **Block public repo creation.**
4. **Lower the default permission.** Set up team grants first so people don't lose write access they need.
5. **Tighten the Actions settings and add rulesets for the production repos.** Check first for workflows that rely on the write token.
