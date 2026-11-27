I haven't changed anything. I couldn't read the skill's identity-and-access reference because permission was denied, and I don't have a shell, so I couldn't query your organization. Below is what's needed and what I'll need from you.

## Why I'm stopping to check first

Turning on **Require two-factor authentication** removes from the organization every member who doesn't have 2FA enabled. Outside collaborators without 2FA lose access too, and so do bot or service accounts without it. Their forks of private repositories go with them. They can be reinstated after they enable 2FA, but this locks out real people, so it needs your approval after we know who would be removed.

## Steps

**1. Find out who would be removed** (this only reads):
```sh
set -euo pipefail
gh api orgs/ORG --jq '{two_factor_requirement_enabled, plan: .plan.name}'
gh api --paginate "orgs/ORG/members?filter=2fa_disabled&per_page=100" --jq '.[].login'
gh api --paginate "orgs/ORG/outside_collaborators?filter=2fa_disabled&per_page=100" --jq '.[].login'
```
You need an organization owner token for this. If the list comes back empty, check that the request succeeded with owner credentials. A token that isn't an owner's can return nothing without an error, which looks the same as everyone having 2FA.

**2. Bring that list down to zero before enforcing.** Tell those people the deadline. Service accounts are the ones that usually get removed by surprise. They should either enable 2FA or be replaced by a GitHub App.

**3. Check whether the enterprise already controls this.** If your organization belongs to an enterprise that enforces 2FA, the setting is managed there. If you use Enterprise Managed Users, 2FA is handled by your identity provider and this setting isn't available.

**4. Turn the requirement on.** `two_factor_requirement_enabled` is read-only in the REST API, so this has to be done in the web interface: **Organization Settings → Authentication security → "Require two-factor authentication for everyone in the organization" → Save**. GitHub then shows the members it will remove, which is one last chance to check before confirming.

**5. Check that it worked:**
```sh
gh api orgs/ORG --jq '.two_factor_requirement_enabled'   # expect true
gh api --paginate "orgs/ORG/members?filter=2fa_disabled&per_page=100" --jq '.[].login'  # expect empty
```
Also check the audit log for the `org.enable_two_factor_requirement` event and any `org.remove_member` entries, so the change has a record.

**6. Related improvements:** enforce SAML single sign-on if your plan supports it, and have your identity provider add and remove members automatically.

## What I need from you
- The organization name, plus either shell access for me or the output of step 1.
- Your OK to go ahead once you've seen the list of accounts that would be removed.
