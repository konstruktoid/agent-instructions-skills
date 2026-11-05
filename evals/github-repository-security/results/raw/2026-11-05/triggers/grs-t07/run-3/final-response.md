I haven't changed anything. The REST API has no endpoint for this setting, so you'll need to enable it in the web UI.

**How to enable it**
1. Open the organization's **Settings → Authentication security**. You need to be an organization owner.
2. Check **Require two-factor authentication for everyone in your organization**.
3. Save.

**Before you save**
- **Non-compliant members are removed.** When you enable the requirement, members and outside collaborators without 2FA are removed from the organization. They can rejoin within three months, and their access and forks are restored, if they turn on 2FA first.
- **Check who is affected first.** In **People**, the member filter **2FA: Disabled** (or `gh api orgs/ORG/members?filter=2fa_disabled`) lists the affected accounts. Ask those people to enable 2FA before you save.
- **Bots and machine accounts need 2FA too.** If any of your automation runs as a user account, it will also be removed. Check for those before you enable the setting.
- **Enterprise-owned organizations** may enforce this at the enterprise level instead. In that case the setting appears under the enterprise policies.

The repository-security skill I have covers single repositories, not organization settings, so it doesn't apply here.

If you give me the organization name and have `gh` authenticated, I can list the members without 2FA. That's a read-only call. I would not make the change itself for you, because it can remove people from the organization.
