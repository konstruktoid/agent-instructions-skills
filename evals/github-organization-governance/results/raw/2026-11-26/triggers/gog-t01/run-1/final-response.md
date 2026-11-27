I couldn't make the change from here. This session has no shell, so I can't run `gh`, and I was blocked from opening the skill's identity-and-access reference file. Below is the plan the skill lays out. Nothing has been read from or changed in your organization yet.

**The REST API can't turn this setting on.** `two_factor_requirement_enabled` on `orgs/ORG` can be read but not written. An organization owner has to switch it on in the web UI. There's also one step that's hard to undo, so check who would be affected first.

### 1. Check before turning it on
Run these with an organization owner token, replacing `ORG` with your organization's name:

```sh
set -euo pipefail
gh api orgs/ORG --jq '{two_factor_requirement_enabled, plan: .plan.name}'
gh api --paginate "orgs/ORG/members?filter=2fa_disabled&per_page=100" --jq '.[].login'
gh api --paginate "orgs/ORG/outside_collaborators?filter=2fa_disabled&per_page=100" --jq '.[].login'
gh api --paginate "orgs/ORG/members?filter=2fa_insecure&per_page=100" --jq '.[].login'   # SMS-only 2FA
```

- **Anyone listed by the `2fa_disabled` queries is removed when you turn the requirement on.** That includes outside collaborators and any bot or service accounts. A removed member can be reinstated within three months, but they lose access and their forks of private repositories in the meantime.
- **Tell those people first and give them a deadline to set up 2FA.** Bot accounts should be replaced with GitHub Apps rather than given 2FA.
- **If your organization is part of an enterprise, check the enterprise setting first.** If the enterprise already requires 2FA, it applies here too and the organization can't loosen it. If you use Enterprise Managed Users, sign-in and 2FA are handled by your identity provider, so this option isn't available.

### 2. Turn it on (organization owner, web UI)
Go to **Settings → Authentication security → Require two-factor authentication for everyone in the organization**. Consider also ticking **Only allow secure two-factor methods**, which rules out SMS. People who only use SMS get a grace period before they're removed.

### 3. Check that it worked
```sh
gh api orgs/ORG --jq '.two_factor_requirement_enabled'          # expect true
gh api --paginate "orgs/ORG/members?filter=2fa_disabled&per_page=100" --jq '.[].login'   # expect empty
gh api "orgs/ORG/audit-log?phrase=action:org.enable_two_factor_requirement" --jq '.[0]'
```
The last command finds the audit log entry that records the change, so you have evidence for later reviews. Reading the audit log through the API requires a plan that includes it (GitHub Enterprise Cloud).

### Related gaps
- **Single sign-on:** if your plan supports SAML single sign-on, enforce it as well.
- **Automatic membership:** add and remove members automatically from your identity provider (SCIM). Otherwise people who leave can keep their access even with 2FA required.

If you send me the organization name and a way to run commands, I can do the checks in step 1 and report who would be removed before you turn it on. Step 2 has to be done by an owner in the web UI.
