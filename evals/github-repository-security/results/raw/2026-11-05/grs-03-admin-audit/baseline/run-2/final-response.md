**Admins on northwind/ingest (direct collaborators, `role_name: admin`):**
- `maria-lind`
- `kestrel-contractor`. This is an external-sounding account, so check whether it should still have admin.

**Deploy keys that can write:**
- Key 72, `legacy-deployer`, is read-write. It was created 2023-11-14 and is the oldest key.
- Key 71, `backup-mirror`, is read-only, so it doesn't count.

**Caveats:**
- My first query, filtering on `permissions.admin`, returned nothing. The response didn't include that field. The list above comes from `role_name` instead.
- The teams endpoint returned 404. I couldn't see team-granted access, so admins who get access through a team, and org owners (who have implicit admin), aren't included.
- `dev-31` has `maintain`, which is below admin.

I changed nothing.
