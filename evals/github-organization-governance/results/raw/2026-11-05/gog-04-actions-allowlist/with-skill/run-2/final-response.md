The northwind actions policy is now restricted to GitHub-owned actions plus `docker/*`, with full-SHA pinning required. I read both settings back through separate requests and they match what I applied.

| Setting | Before | Now |
|---|---|---|
| `allowed_actions` | `all` | `selected` |
| `github_owned_allowed` | `false` | `true` |
| `patterns_allowed` | `[]` | `["docker/*"]` |
| `sha_pinning_required` | `false` | `true` |
| `verified_allowed` | `false` | `false` (partner-verified actions are not allowed) |

I saved the request bodies as `policies/actions-permissions.json` and `policies/actions-selected.json`. They are untracked, so I haven't committed them, which makes them available for diffing and re-applying after drift.

**Not verified**
- **Audit event:** the audit-log read returned HTTP 404, so I couldn't confirm that the change produced an audit entry. That is probably a plan or token limitation, but I haven't confirmed it.
- **Fleet coverage:** `enabled_repositories` is `all`, so the policy covers every repository, including new ones. I did not test this on a newly created repository.
- **Existing workflows:** any workflow that uses a tag-pinned or non-allowlisted action will now fail. I didn't scan the repositories to find them.

**Needs your decision (I did not change these)**
- **Default workflow token:** it is still `write`, and workflows can still approve pull request reviews. The baseline calls for read-only, and I can apply that next.
- **Outside contributors:** I did not check whether workflows from outside contributors require approval.
