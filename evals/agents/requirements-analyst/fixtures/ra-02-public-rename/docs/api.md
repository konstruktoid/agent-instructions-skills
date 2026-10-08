# Public API

Names listed here follow semantic versioning: a change that breaks one waits for the next
major release.

| Name | Status | Description |
|---|---|---|
| `userclient.fetch(user_id)` | stable | Return the user record for `user_id`. |
| `userclient.sync_all()` | stable | Refresh every cached user. |
| `userclient.client.build_url` | internal | Not covered by the compatibility promise. |
