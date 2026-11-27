I couldn't run the review here, so I don't have any results yet. This session has no shell, so I can't call `gh api`, and my request to read the skill's app-policy reference (`references/policies.md`) was declined. I also don't know your org's name.

If you run the commands below with an **org owner** token and paste the output back, I'll write up the findings. Replace `ORG` with your org name.

**1. List every installed app and its scope:**
```sh
gh api --paginate "orgs/ORG/installations?per_page=100" --jq '.installations[] |
  {id, app_slug, repository_selection, permissions, events, created_at, updated_at, suspended_at}'
```

**2. For each app installed on selected repositories only, list which ones.** This endpoint needs the app's own installation token, so as an owner you check this on the installation's settings page instead:
```
https://github.com/organizations/ORG/settings/installations/<installation id>
```

**3. Related settings that decide what can act on your repositories:**
```sh
gh api --paginate "orgs/ORG/personal-access-tokens?per_page=100" --jq '.[] |
  {owner: .owner.login, repository_selection, permissions, token_expires_at, token_last_used_at}'
gh api --paginate "orgs/ORG/personal-access-token-requests?per_page=100" --jq '.[] |
  {owner: .owner.login, reason, created_at}'
```

**What I'll check each app against:**
- **Access to all repositories.** Any app with access to every repo, including ones created later, should either need that or be cut down to selected repositories.
- **Write permissions that are higher than needed.** I'll flag write access to `administration`, `contents`, `workflows`, `secrets`, `members` and `organization_administration`, since these let an app change code, CI or access. Each one needs a stated reason.
- **Owner and last use.** Every app should have an owning team and a reason it's there. Apps nobody claims, or that look unused (e.g. `updated_at` is old), are candidates for removal.
- **Suspended installations.** These should either be removed or come with a reason.
- **Tokens instead of apps.** Fine-grained personal access tokens doing automation work should move to an app or OIDC. Any token without an expiry is a finding. Classic tokens are always a finding.

**What these commands can't show:** OAuth apps that members have authorized, and whether OAuth app access restrictions are turned on, are only visible on the org's **Settings → Third-party access** page. I'll mark those as not checked unless you send them.

I won't change anything until you approve it. Suspending or uninstalling an app, or reducing what it can access, affects the people who rely on it, so I'll treat each one as a separate proposal.
