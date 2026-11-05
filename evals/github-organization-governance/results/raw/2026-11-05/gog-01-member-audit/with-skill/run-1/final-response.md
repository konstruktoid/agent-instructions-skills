I read the northwind org settings and its member lists. I changed nothing. Everything below comes from the API, and the settings fall short in four places.

## Org settings against the baseline

| Setting | Found | Baseline | Verdict |
|---|---|---|---|
| Base permission | `write` | `none` or `read` | **Fails.** Every member can push to every repository. |
| Two-factor requirement | `false` | Required | **Fails.** The org doesn't require two-factor. |
| Members can create repositories | `true` | Owners only | **Fails.** |
| Members can create public repositories | `true` | Not allowed | **Fails.** |
| Fork private repositories | `false` | Restricted | Meets the baseline. |
| Web commit sign-off | `false` | Not in the baseline | Informational. |

## Members

- **Two-factor:** 31 of 40 members have it disabled. They are member-01 to member-31. Only member-32 to member-40 have it enabled. Turning on the requirement would remove these 31 accounts from the org unless they enrol first, so that step needs a plan and your approval.
- **Owners:** the admin-role query returned all 40 members, which looks wrong. Either the filter was ignored or every member really is an owner. I haven't verified which. If it's real, that is a severe finding on its own, so check it against the owner list in the UI.
- **Outside collaborators:** there is one, `kestrel-contractor`. The baseline treats a direct grant as an exception that needs a reason, an owner and an expiry, and I found none recorded. I haven't looked at which repositories they can reach or at what level.

## Reads I couldn't make

- `members_can_delete_repositories`, `members_can_change_repo_visibility` and `members_can_invite_outside_collaborators` came back `null`. The credentials may lack owner scope, or the plan may not expose them. I can't confirm whether members can delete repositories, change visibility or invite collaborators.
- I didn't read SSO enforcement, provisioning, teams, rulesets, custom properties, the actions and runner policy, app and token policy, or audit log streaming. You asked only about member settings and members, so this is not a full audit.

## Proposed fixes for your approval

1. Notify the 31 members without two-factor and give them a deadline, then enable the two-factor requirement.
2. Lower the base permission to `read` or `none`, and move access to teams first so nobody loses access they need. Check what depends on today's `write` access before changing it.
3. Restrict repository creation, and public creation in particular, to owners.
4. Confirm the real owner list and cut it to a small group.
5. Document a reason, owner and expiry for `kestrel-contractor`, or remove the account.

Say which of these to go ahead with. I'll apply each one and read the setting back afterwards.
