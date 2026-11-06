I can't turn this on from here, and you'd want to be careful before doing it yourself.

**Why I can't do it**
- Requiring 2FA is an organization-level setting. The repository-security skill I have only covers single repositories.
- As far as I know, GitHub's REST API only reports `two_factor_requirement_enabled`. It doesn't let you set it, so the change has to be made in the web UI.
- I also have no shell or `gh` access in this session, and I don't know your organization's name.

**Steps (an organization owner has to do these)**
1. Go to `https://github.com/organizations/<ORG>/settings/security`. You can also open the organization, then **Settings**, then **Authentication security**.
2. Check **Require two-factor authentication for everyone in your organization**.
3. Review the list of members and outside collaborators who don't have 2FA enabled.
4. Save the change.

**What to know before you save**
- Members and outside collaborators without 2FA are removed from the organization automatically. They lose access to private repositories and forks. GitHub can restore their access if they enable 2FA within three months.
- Before enforcing, check who is affected. Run `gh api orgs/<ORG>/members?filter=2fa_disabled --paginate --jq '.[].login'` (and `outside_collaborators?filter=2fa_disabled` for outside collaborators). Then give those people notice.
- Bot and machine accounts without 2FA will be removed too. Check for them first.
- Enforcement is an outward-facing change that's hard to undo cleanly, so I'd rather you confirm the timing.

If you tell me the organization name, I can help draft the notice to affected members. If you run the audit commands and paste the output, I can help interpret it.
