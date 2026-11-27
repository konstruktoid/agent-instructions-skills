I can't make this change from here. I have no shell to run `gh`, I couldn't open the skill's identity-and-access reference because permission was denied, and I don't know your organization's name. Here's the plan. Run the reads and send me the output, and I'll check it and do the read-back.

## 1. Check who would lose access (do this first)

Turning on the requirement **removes every member and outside collaborator who doesn't have 2FA set up**, and cancels their pending invitations. Removed people lose access to private forks, and you have to re-invite them. Run these with an organization owner token. They don't change anything:

```sh
set -euo pipefail
ORG=your-org
gh api "orgs/$ORG" --jq '{two_factor_requirement_enabled, plan: .plan.name}'
gh api --paginate "orgs/$ORG/members?filter=2fa_disabled&per_page=100" --jq '.[].login'
gh api --paginate "orgs/$ORG/outside_collaborators?filter=2fa_disabled&per_page=100" --jq '.[].login'
```

- If either list isn't empty, ask those people to turn on 2FA before you enable the requirement, or accept that they'll be removed.
- Bot and service accounts count too. If an automation account gets removed, whatever runs as it breaks. Moving it to a GitHub App is the long-term fix.
- If you use Enterprise Managed Users, this setting doesn't apply. 2FA is enforced at your identity provider, so check there instead.
- If the organization belongs to an enterprise that already requires 2FA, the setting is inherited and you can't change it from inside the organization.

## 2. Turn it on (needs your go-ahead)

The REST API only lets you read `two_factor_requirement_enabled`, not change it, so this is done in the web UI:

**Organization → Settings → Authentication security → Require two-factor authentication** (you can also tick "Only allow secure two-factor methods" to block SMS) → **Save**.

If you're an owner without 2FA yourself, GitHub won't let you save this. Because it removes people, I'd want your explicit approval after you've seen the list from step 1.

## 3. Check it took effect

```sh
gh api "orgs/$ORG" --jq '.two_factor_requirement_enabled'      # expect true
gh api --paginate "orgs/$ORG/members?filter=2fa_disabled&per_page=100" --jq '.[].login'  # expect empty
gh api --paginate "orgs/$ORG/audit-log?phrase=action:org.enable_two_factor_requirement" --jq '.[] | {action, actor, created_at}'
```

The last command finds the audit log entry for the change, which is your evidence for an audit. It needs a plan that includes audit log API access. If your plan doesn't, say so rather than treating the check as passed.

## 4. Related next steps

- Turn on single sign-on (SSO) if your plan supports it.
- Have your identity provider add and remove members automatically, so 2FA and SSO cover people from the day they join.

Tell me the organization name and paste the step 1 output, and I'll tell you who would be removed and what to do about each person before you switch it on.
