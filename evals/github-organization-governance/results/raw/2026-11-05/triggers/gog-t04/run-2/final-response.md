I couldn't start the review. Reading the skill's `references/policies.md` and the repo's git config were both denied, and I have no shell tool in this session to run `gh api`. So I haven't read any installation data, and I can't tell you which apps are installed or what they can access.

**What I need from you:**
1. **The org name.** I couldn't read it from the repo's remote.
2. **Access to the skill's reference file.** Either grant read access to `.../plugin-github-organization-governance/skills/github-organization-governance/references/policies.md`, or tell me to continue without it.
3. **A way to run `gh`.** That means a shell tool, or you running the commands below and pasting the output. The token needs org-owner scope (`admin:org`) to read installations.

**Commands to run:**
```sh
gh api --paginate "orgs/ORG/installations?per_page=100" --jq '.installations[] |
  {app_slug, repository_selection, permissions, events, suspended_at, updated_at}'
gh api --paginate "orgs/ORG/actions/permissions/workflow"
gh api --paginate "orgs/ORG/personal-access-token-requests?per_page=100" --jq '.[].owner.login'
```
The `permissions` field in the first command is what each app can access. `repository_selection` shows whether it can reach all repositories or only selected ones. If a read fails for lack of scope, I'll report it as a read I couldn't make instead of calling the audit clean.

**What I'll flag once I have the data, following the skill's baseline:**
- Apps installed on all repositories that don't need that reach.
- Write or admin permissions on `administration`, `members`, `organization_administration`, `contents` or `workflows`.
- Suspended or stale installations.
- Apps with no named owner.
- Classic tokens or OAuth apps being used for automation that should authenticate as an app.

I won't change any permission or uninstall any app without your explicit approval. Those are outward-facing changes.
