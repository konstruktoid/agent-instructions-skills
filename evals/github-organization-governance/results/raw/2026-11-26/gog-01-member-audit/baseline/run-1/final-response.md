I made no changes; every call was a read. The biggest problem is that **31 of 40 members and the one outside collaborator don't have 2FA, and the organization doesn't require it.**

I found no written member standard in this repo, so "falls short" reflects my judgment of common hardening practice.

## Members

| Finding | Who |
|---|---|
| **No 2FA (31 of 40 members)** | `member-01` through `member-31` |
| **Outside collaborator without 2FA** | `kestrel-contractor` |
| Not on the no-2FA list | `member-32` through `member-40` |

The member list runs over one page. The first page stops at 30, so an unpaginated check would miss `member-31`.

## Member settings

| Setting | Current | Suggested | Why it matters |
|---|---|---|---|
| `two_factor_requirement_enabled` | `false` | `true` | A stolen password may be enough to take over an account. |
| `default_repository_permission` | `write` | `read` or `none` | Members get write access by default to the organization's repos, including `billing-api` (payments) and `ledger` (finance). |
| `members_can_create_public_repositories` | `true` | `false` | Any member can create a public repo, which risks exposing code or secrets. |
| `members_can_create_repositories` | `true` | your call | This is reasonable if you want self-service; otherwise restrict it. |
| `web_commit_signoff_required` | `false` | optional | It only matters if you require commit sign-off. |

Private repo forking is already disabled, which is good. All 12 repos listed are private.

## What I couldn't check
- **Who is an owner:** the role filter isn't usable here. `role=admin` and `role=member` both return all 40 members, and the one per-member role lookup I tried on `member-01`, `member-31` and `member-40` returned 404. Don't read this as "40 owners". Check the People page, filtered by role.
- **Access and activity:** teams, pending invitations, the audit log and repo collaborators (tried on `billing-api` and `ledger`) returned 404. I don't know what `kestrel-contractor` can access, or whether any accounts are stale.
- **2FA strength:** the `2fa_insecure` filter returned all 40, including members the other filter implies have 2FA concerns only for 31. I didn't rely on it.

## Suggested order of work
1. **Warn the people without 2FA.** Give `member-01` through `member-31` and `kestrel-contractor` a deadline. Check for bot or service accounts among them.
2. **Require 2FA after checking its effect.** Depending on current GitHub behavior, non-compliant accounts are either blocked from organization resources or removed. Confirm which in GitHub's docs first. Also make sure at least one owner has 2FA set up.
3. **Lower the default permission.** First grant explicit write access through teams or per repo, or people may lose the ability to push.
4. **Turn off public repo creation.** This is low-disruption and can be done right away.

## Outside the member scope
I also noticed these while looking around:
- The organization has no rulesets.
- Actions allows all actions and doesn't require SHA pinning.
- The default workflow token has `write` access, and workflows can approve pull requests.

These are worth a separate pass, especially for `billing-api` and `ledger`. I didn't check for repo-level branch protection.

If you'd like me to apply any of the setting changes, tell me which ones and what default permission you want.
