On `northwind/ingest`, two users have admin and one deploy key can write. I only read data and changed nothing.

**Admins**
- `maria-lind`
- `kestrel-contractor`

`dev-31` has the `maintain` role, which is below admin. The other 31 collaborators have write access or less. The API returned no `permissions` object here, so I went by `role_name`.

**Deploy keys with write access**
- ID 72, `legacy-deployer`. It is read-write and was added on 2023-11-14. The API didn't say who added it.

The other deploy key, ID 71 `backup-mirror`, is read-only.

`kestrel-contractor` looks like an external account, and the 2023 `legacy-deployer` key is old. Check that both are still needed.

I used the collaborators endpoint with its default `affiliation=all`. That should include admin access that comes through teams or org ownership, but I didn't check team memberships separately.
