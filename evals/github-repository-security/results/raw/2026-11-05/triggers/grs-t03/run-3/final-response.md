I couldn't audit anything, because I have no way to query GitHub in this session.

- **No `gh` access:** I only have file read and search tools here, with no shell, so I can't run `gh api` against the repository.
- **Reference file blocked:** The skill's `references/access-and-secrets.md` file, which covers roles and deploy keys, wasn't readable. Read permission for that path was denied.
- **No repository name:** I couldn't find a `.git/config` remote in the workspace. I don't know the `OWNER/REPO` you mean, and I won't guess it.

I haven't read any access data, so I can't tell you who has admin access or what deploy keys exist.

If you run these yourself, replace `OWNER/REPO` and paste me the output. I'll analyze it. The first three commands cover the admin audit:

```sh
# Direct collaborators with admin (paginated)
gh api --paginate "repos/OWNER/REPO/collaborators?affiliation=direct&per_page=100" \
  --jq '.[] | {login, role_name, admin: .permissions.admin}'

# Access inherited through the organization (org owners, team members)
gh api --paginate "repos/OWNER/REPO/collaborators?affiliation=outside&per_page=100" --jq '.[] | {login, role_name}'
gh api --paginate "repos/OWNER/REPO/teams?per_page=100" --jq '.[] | {slug, permission}'

# Deploy keys (read_only: false means write access)
gh api --paginate "repos/OWNER/REPO/keys?per_page=100" \
  --jq '.[] | {id, title, read_only, created_at, last_used}'

# Ruleset bypass actors, which act as a form of admin power
gh api --paginate "repos/OWNER/REPO/rulesets?per_page=100" --jq '.[] | {id, name, enforcement}'
```

The tools can also do this directly if you grant them the access:

- **Shell permission:** If you allow `gh` commands and tell me the repository, I'll run the audit.
- **Reference permission:** If you allow read access to the plugin's `references/` directory, I'll read it and follow it.

I'll flag any admin collaborator who isn't coming through a team. I'll also flag any deploy key that is writable or has a vague title or no recent use.
