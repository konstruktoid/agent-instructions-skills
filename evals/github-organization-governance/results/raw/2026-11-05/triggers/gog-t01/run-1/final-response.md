I couldn't enable the two-factor requirement. I haven't changed anything yet, and a few things block me.

**What blocked me**
- **Reference file:** The governance skill says to read `references/identity-and-access.md` before changing two-factor settings. I wasn't given permission to read that file, so I haven't applied its guidance.
- **Organization name:** You didn't say which organization this is, and nothing in the workspace names it. I need the `ORG` slug.
- **Approval:** Requiring 2FA is an organization-wide change that can remove access. Members without 2FA are removed from the organization when it is enabled. The skill requires your explicit approval before I apply it.

**What I'd do once you've answered those**
1. **Read the current state.** I'd run `gh api orgs/ORG --jq '.two_factor_requirement_enabled'`. I'd also list the members who would be affected: `gh api --paginate "orgs/ORG/members?filter=2fa_disabled&per_page=100" --jq '.[].login'`. This needs an owner-level token.
2. **Show you the list.** If any members have 2FA disabled, I'd name them. Enforcing the requirement removes them, so you may want to warn them first.
3. **Apply the setting after you approve.** The REST API doesn't reliably expose this toggle. If it can't be set that way, the setting is at **Organization → Settings → Authentication security → Require two-factor authentication**. I'd tell you which route was needed.
4. **Read it back.** I'd confirm in a separate request that `two_factor_requirement_enabled` is `true`. I'd also check the audit log for the matching event, if your plan includes audit log access.

**What I need from you**
- The organization slug.
- Permission to read the skill's reference files.
- Confirmation that you're an organization owner and that removing non-compliant members is acceptable.

If your organization is on an enterprise account, the enterprise may already enforce 2FA or constrain this setting. I'll check that too.
