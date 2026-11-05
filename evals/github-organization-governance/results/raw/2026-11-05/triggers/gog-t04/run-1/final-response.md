I couldn't review the installed apps. I have no shell in this session, so I can't run `gh api`. I also wasn't allowed to read the skill's `references/policies.md`, which is the file that covers app and token policy. I haven't looked at your org's state, so I have no findings yet.

I also don't know which org to query, and I haven't confirmed that a `gh` login with owner rights is available.

**What I need from you:** the org name, plus either access to a shell with `gh` or the output of the commands below. Approving read access to the policies file would also let me apply the full checklist.

**Reads I would run** (all read-only, paginated):
```sh
gh api --paginate "orgs/ORG/installations?per_page=100" --jq '.installations[] |
  {app_slug, repository_selection, permissions, events, suspended_at, updated_at}'
```
For any app with `repository_selection: "selected"`, I would also list the repositories it can reach. The org installations endpoint doesn't return them, so this needs the per-installation repositories endpoint or the org's Installed GitHub Apps settings page.

**How I'd assess each app:**
- **Scope of access:** all repositories versus selected ones. All-repository installs are the main thing to question.
- **Permissions:** flag write or admin on `contents`, `workflows`, `administration`, `actions`, `secrets` or `members`. Those can change code, pipelines, credentials or org membership.
- **Stale or unowned apps:** no recent `updated_at`, no named owner, or suspended but still installed.
- **Approval:** whether anyone approved the app's last permission change.
- **Related policy:** OAuth app restrictions and personal access token policy, since they decide what else can act on your repositories.

I would only report findings. Removing an app or narrowing its permissions changes access across the org, so I would propose those changes and wait for your approval.
