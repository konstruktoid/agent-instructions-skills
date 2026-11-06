I read the northwind member settings and member list, and nothing has been changed. The org falls short of the baseline on five settings, and 31 of its 40 members have two-factor authentication off.

## Settings that fall short

| Setting | Current | Baseline |
|---|---|---|
| Base permission (`default_repository_permission`) | `write` | `none` or `read` |
| Two-factor requirement | `false` | required for every member |
| Members creating repositories | allowed | restricted to owners, or provisioned with required classification |
| Members creating public repositories | allowed | not allowed |
| Web commit sign-off | not required | worth enabling (a recommendation, not a baseline item) |

- **Base permission `write`:** every member can push to every repository that rulesets don't protect. The fix is a migration: find the teams that rely on implicit access, grant it explicitly, then lower the base.
- **Public repository creation:** this is the largest exposure in the settings.
- **Private-repository forking:** this is already disabled, which meets the baseline.

## Members

- **2FA disabled:** 31 of 40 members (`member-01` to `member-31`) have 2FA off. Because the requirement isn't enforced, any member could be added or re-enabled without it. Turning on enforcement removes non-compliant members until they enrol, so you should warn them first.
- **Outside collaborator:** `kestrel-contractor` has direct access. The baseline treats this as an exception that needs a reason, an owner and an expiry. I found none recorded.
- **Owners:** I could not establish who the owners are. The `role=admin` filter returned all 40 members, which looks like the filter being ignored, and `memberships/{user}` returned 404. Owner count and owner 2FA are unverified.

## Reads that did not return data

- `members_can_delete_repositories`, `members_can_change_repo_visibility` and `members_can_invite_outside_collaborators` came back `null`. These fields usually need an owner token, so I can't say whether members can delete, change visibility or invite collaborators.
- I did not read the following, so this is a partial audit of member settings only, and it should not be read as a clean result for anything beyond them:
  - SSO enforcement and provisioning
  - actions and runner policy
  - app installations
  - token policy
  - rulesets
  - custom property coverage
  - audit log streaming and retention

## Proposed changes (need your approval, nothing applied)

1. Set base permission to `read` after mapping team access.
2. Disallow public repository creation, and decide whether to restrict private creation too.
3. Require 2FA, after notifying the 31 affected members.
4. Document or remove `kestrel-contractor`'s access.
5. Re-read the `null` fields with an owner token.

I can start on any of these when you approve. I'd also suggest a wider audit covering the areas listed above.
