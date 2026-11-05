I read the `northwind` member settings and member list without changing anything. The settings fall short of the baseline in several places, and 31 of the 40 members have no two-factor authentication.

**Organization settings**

| Setting | Current | Baseline | Status |
|---|---|---|---|
| Two-factor requirement | `false` | required | Falls short |
| Base repository permission | `write` | `none` or `read` | Falls short |
| Members can create repositories | `true` | owners only | Falls short |
| Members can create public repositories | `true` | no | Falls short |
| Forking private repositories | `false` | n/a | Fine |
| Web commit sign-off | `false` | not in the baseline | Noted only |

I did not read any setting for members changing repository visibility, deleting repositories or transferring them. The two repository-creation fields above are the only member-privilege fields I read.

**Members**
- **Two-factor:** 31 of 40 members (`member-01` to `member-31`) have 2FA disabled. The org-level requirement is also off, so nothing stops new members joining without it.
- **Owner role:** all 40 members come back from the admin filter, so every member is an organization owner. That is far too broad. Owners can change every setting here, and the base permission and creation settings are moot when everyone is an owner. I'd confirm this is real and not an artifact of the filter, then treat it as the biggest finding.
- **Outside collaborator:** there is one, `kestrel-contractor`. I did not check which repositories they can reach, so I can't say whether they have a recorded reason or an expiry.

**Actions policy** (found while I was in the org settings)
- **Default workflow token:** it is `write`, not read-only.
- **Approving pull requests:** workflows can approve pull request reviews (`can_approve_pull_request_reviews: true`).
- **Allowed actions:** the policy is `all`, with no allowlist and no SHA pinning required.

**Reads I couldn't make or didn't make**
- **Pending invitations:** the endpoint returned 404, so I can't say whether any are outstanding.
- **Skipped:** I did not read single sign-on or provisioning, rulesets, custom properties, app installations, runner groups, or the audit log. This is a member audit only, so it is not a full org audit.
- **Outside collaborator list:** my first attempt was a malformed query. The rerun worked and returned the one name above.

The workspace's `policies/` and `rulesets/` folders contain only README files, so there is no committed definition to compare the live state against.

**Proposed fixes, not applied** (each one needs your approval)
1. Require 2FA org-wide. Removing the 31 members who haven't enabled it is outward-facing, so I would notify them first.
2. Set the base permission to `read` or `none`, and move access to teams.
3. Restrict repository creation, with public creation owner-only.
4. Cut the owner list down to a small named group.
5. Set the default workflow token to read-only, turn off workflow PR approval, and add an actions allowlist.
6. Review `kestrel-contractor`'s access and give it a reason and an expiry.

Tell me which of these to apply and I'll make the changes and read each one back.
