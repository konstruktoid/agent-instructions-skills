The `northwind` actions policy now allows only GitHub-owned actions and anything under `docker/`, and it requires actions to be pinned to a full commit SHA. I read both settings back through separate requests, and they match what I set.

| Setting | Before | Now |
|---|---|---|
| `allowed_actions` | `all` | `selected` |
| `github_owned_allowed` | `false` | `true` |
| `patterns_allowed` | none | `docker/*` |
| `verified_allowed` | `false` | `false` (partner-verified actions stay blocked) |
| `sha_pinning_required` | `false` | `true` |

I saved the two request bodies as `policies/actions-permissions.json` and `policies/selected-actions.json` in the workspace. I haven't committed them, so you can review them and reapply them if the settings drift.

**Checks I didn't run:**
- **Existing workflows:** I didn't check what workflows already call. Any that use a non-allowlisted action or a tag-pinned reference, such as `actions/checkout@v4`, will fail until they're pinned to a full SHA. Workflows that use `docker/*` actions also need SHA pins now.
- **Audit event:** I didn't confirm that the change produced an audit log entry.

**Not changed, because you didn't ask:** the default workflow token is still `write`, and workflows can still approve pull request reviews. The skill's baseline calls for a read-only token. I can tighten both if you want.
