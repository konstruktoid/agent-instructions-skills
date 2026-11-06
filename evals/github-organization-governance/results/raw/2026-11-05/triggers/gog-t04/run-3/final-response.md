I couldn't review your org's GitHub Apps. I have no way to query GitHub in this session, so nothing below comes from your org's data.

- **No shell access.** This session has no Bash tool, so I can't run `gh api`, and I have no GitHub MCP tool either.
- **Reference file blocked.** The skill's `references/policies.md` covers app installation rules. I was denied permission to read it, so I haven't applied it.
- **Org name unknown.** I don't know which org to query.

**Run these yourself.** Use an org-owner token and replace `ORG` with your org name. Paste the output here and I'll review it.

```sh
# Installed apps and whether each has all-repo or selected-repo access
gh api --paginate "orgs/ORG/installations?per_page=100" --jq '.installations[] |
  {id, app_slug, repository_selection, permissions, events, suspended_at, updated_at}'

# For each app on "selected" access, see which repos it reaches
gh api --paginate "user/installations/INSTALLATION_ID/repositories"
```

The first command lists each installed app, its permission scopes, and whether it covers all repositories or only selected ones. It also shows whether the app is suspended and when it last changed. The second command lists the repositories one app can reach. It needs a user token that can see the installation. For installations you manage as an org owner, the **Settings → GitHub Apps** page shows the same information.

**What I'll check once I have the output**, against the governance baseline:
- Apps with `repository_selection: all` that could be narrowed to named repositories.
- Broad permissions such as `administration`, `contents: write`, `secrets`, `workflows` and `members`.
- Apps that are suspended, no longer used or not updated in a long time.
- Unknown or unvetted publishers.
- Automation that still uses classic tokens or PATs where a scoped app or OIDC would do.

If you want me to run the reads directly, enable a shell tool or allow the `gh` commands. If you also want me to read the skill's `policies.md`, grant that permission and give me the org name.

I haven't changed anything. Narrowing an app's access or removing an app would need your explicit approval first.
