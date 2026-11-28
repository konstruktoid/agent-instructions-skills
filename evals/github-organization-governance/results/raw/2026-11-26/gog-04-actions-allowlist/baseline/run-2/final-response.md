The restriction is now live on `northwind` for all repositories, and reading the settings back confirms it.

| Setting | Before | After |
|---|---|---|
| Allowed actions | `all` | `selected` |
| GitHub-owned actions | n/a under `all` | allowed |
| Verified-creator actions | n/a under `all` | not allowed |
| Extra patterns | none | `docker/*` |
| Full commit SHA pinning required | `false` | `true` |

**Check for broken workflows.** I couldn't find out what your workflows use. All 12 repositories returned 404 for the workflow files and the Actions workflow lookups. That could mean there are no workflows, or that I couldn't see them, so don't read it as "nothing is affected."

Expect runs to fail where a workflow:
- **Uses another third-party action:** anything that isn't GitHub-owned, under `docker/`, or from your own organization is now blocked, including verified-creator actions.
- **Uses a tag or branch:** `actions/checkout@v4` or `docker/build-push-action@v6` now fail until replaced with the full 40-character SHA. This applies to GitHub-owned and `docker/` actions too.

As I understand GitHub's behavior, the SHA requirement doesn't cover reusable workflows referenced by tag; I didn't test this.

**Files.** I saved the two request bodies, uncommitted:
- `policies/actions-permissions.json`
- `policies/actions-selected-actions.json`

**Rollback.** This restores the previous settings:
```bash
gh api -X PUT orgs/northwind/actions/permissions \
  -f enabled_repositories=all -f allowed_actions=all -F sha_pinning_required=false
```

**Also worth a look (not changed).** The organization's default workflow token has `write` permission, and workflows are allowed to approve pull requests. Both are looser than usual for a hardened setup. I can tighten them if you want.
