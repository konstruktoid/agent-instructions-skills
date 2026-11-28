I couldn't do the review myself. I can't run commands in this session, so I can't call the GitHub API. I also wasn't given permission to open the skill's reference file on app policy. I don't know your org's name either, so I haven't looked at any installations yet.

Here's how to collect the data. Replace `ORG` with your org's name. You need an org-owner token, because the installations endpoint shows nothing to anyone with less access. Paste the output back and I'll do the review.

```sh
set -euo pipefail
ORG=your-org
out="$(mktemp -d)"

# 1. Every installed app, with its permissions, subscribed events and repository scope
gh api --paginate "orgs/$ORG/installations?per_page=100" \
  --jq '.installations[] | {id, app_slug, repository_selection, permissions, events,
        created_at, updated_at, suspended_at}' > "$out/installations.json"

# 2. For each app limited to selected repositories, which repositories it can reach
#    (this endpoint has to be called with the app's installation token, so use step 3 instead)

# 3. The same per-installation repository list, as the org owner sees it in the UI:
#    https://github.com/organizations/$ORG/settings/installations
#    → Configure on each app shows "All repositories" or the list of selected ones

# 4. OAuth app access policy and token policy, for comparison
gh api "orgs/$ORG" --jq '{plan: .plan.name, two_factor_requirement_enabled}' > "$out/org.json"

wc -l "$out"/*.json
```

**What I'll check each app for:**

1. **Repository scope.** `repository_selection: "all"` gives the app every repository, including ones created later. Only org-wide tools need that (CI, security scanning). Anything else should be limited to the repositories it actually uses.
2. **Write permissions.** I'll flag write or admin access to these permissions:
   - `administration`
   - `contents`
   - `workflows`
   - `secrets`
   - `actions`
   - `members`
   - `organization_administration`

   Each one needs a reason that matches what the app does. For example, a linter has no reason to hold `contents: write` or `workflows: write`.
3. **Event subscriptions.** Events the app doesn't need still send data to whoever runs the app.
4. **Staleness.** I'll flag apps that are suspended, that haven't been updated in a long time, or that have no clear owning team. Each one should be removed or given an owner.
5. **Who runs the app.** An app you build yourselves is controlled by you. A Marketplace or third-party app sends data to its vendor, so its scope should be held to a stricter standard.
6. **Change history.** If you have audit log access, I'll check `integration_installation.*` and `integration_installation_request` events. They show who installed or widened each app, and when.

**Output:** a table with one row per app showing its scope, permissions, findings and a proposed change. Each proposal will be one of three things: limit it to selected repositories, remove a permission (which the app's owner has to do), or uninstall it.

I won't change anything without your approval. Every proposal changes what an app can reach, and you approve each one separately.

If you'd like me to run all of this myself, give this session shell access and tell me the org name.
