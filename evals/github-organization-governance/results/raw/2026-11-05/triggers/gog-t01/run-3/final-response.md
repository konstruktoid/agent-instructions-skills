I haven't changed anything yet. I can't make this change in this session, and I need two things from you before I can proceed.

**Why I'm blocked**
- I have no shell tool here, so I can't run `gh api` to read or change the organization.
- You haven't granted me read access to the skill's `identity-and-access.md` reference, which covers the two-factor rollout details.

**What I need**
1. **The organization name.** I don't know which org this is.
2. **Confirmation to enforce.** Turning on required 2FA is outward-facing. Members without 2FA are removed from the org when it takes effect, and they lose access until they enable it and are reinvited. I won't apply it without your explicit go-ahead.

**Plan once I can run `gh`**
1. **Read the current state.**
   - Check `two_factor_requirement_enabled` on `orgs/ORG`.
   - List members who are missing 2FA with `gh api --paginate "orgs/ORG/members?filter=2fa_disabled&per_page=100" --jq '.[].login'`.
   - Check whether an enterprise policy already controls this setting.
   - This needs an org owner token. I'll tell you if any read fails, rather than report a clean result from a partial check.
2. **Give you the list of members who would be removed.** I'll suggest notifying them first so nobody loses access by surprise. Bots and outside collaborators also need checking.
3. **Apply the setting after you confirm.** I'll run `gh api -X PATCH orgs/ORG -F two_factor_requirement_enabled=true`.
4. **Read it back with a separate request.** This is because an accepted request isn't proof the setting applied. I'll also check the audit log for the change event, if your plan includes audit log access.
5. **Look at SSO and provisioning.** The baseline also calls for single sign-on and automated provisioning where your plan supports them.

You can also turn it on yourself in the GitHub UI. Go to Org Settings → Authentication security → "Require two-factor authentication for everyone in your organization".

Please tell me the org name and whether to proceed. If you want me to use the skill's reference files, please also grant read access to that directory. A shell tool would let me run the `gh` commands.
