I haven't changed anything. The tools I have here can only read and search local files, so I can't call the GitHub API or settings. The repository-hardening skill I do have covers a single repository, not organization-wide settings.

Turning this on is also disruptive. **Members and outside collaborators without 2FA are removed from the organization** when the requirement is enforced, and they lose access to its repositories and forks. Before you enforce it, I'd check who is affected.

**1. Find who doesn't have 2FA** (needs org owner rights):
```bash
gh api --paginate "orgs/<ORG>/members?filter=2fa_disabled" --jq '.[].login'
gh api --paginate "orgs/<ORG>/outside_collaborators?filter=2fa_disabled" --jq '.[].login'
```

**2. Warn those people** and give them time to enable 2FA.

**3. Enforce the requirement.** This is a web UI setting only, with no public REST endpoint:
- Open `https://github.com/organizations/<ORG>/settings/security`.
- Under **Authentication security**, check **Require two-factor authentication for everyone in your organization**.
- Optionally restrict it to secure methods such as security keys, passkeys or authenticator apps, which excludes SMS.

**4. Check afterwards** by re-running the commands in step 1. Both lists should be empty. Anyone removed can be reinstated for 3 months after they enable 2FA.

If you give me the org name, I can draft the notice to members. If you'd rather I run the checks, run `gh` yourself and paste the output. Tell me when you've reviewed the affected list and are ready to enforce.
