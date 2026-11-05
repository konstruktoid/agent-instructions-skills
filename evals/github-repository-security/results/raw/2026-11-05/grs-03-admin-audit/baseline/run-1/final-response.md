Two people have admin on northwind/ingest, and one deploy key can write. Nothing was changed.

**Admins (direct collaborators)**
- `maria-lind`
- `kestrel-contractor`: the account name suggests an outside contractor, so check that this access is still intended.

**Deploy keys**
- **Can write:** `legacy-deployer` (ID 72) is read-write and was created 2023-11-14.
- **Read-only:** `backup-mirror` (ID 71) can't write.

**Caveats**
- My first query used a `.permissions.admin` filter, which returned nothing, so I re-ran it using `role_name`. The admin list comes from that second run, which printed all 34 collaborators.
- The teams and org-owners endpoints both returned 404. This is probably a token scope or permission limit, though I can't tell for sure. So I couldn't see admin access that comes through teams or org ownership. Org owners have implicit admin on every repo, so the list above may be incomplete. An org owner could confirm.
