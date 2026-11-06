**Admins on northwind/ingest** (direct and outside collaborators, read across all pages):
- `maria-lind` (admin)
- `kestrel-contractor` (admin). The login suggests an external contractor. It's worth confirming that this person needs admin.

The other 31 collaborators hold lower roles. `dev-01` through `dev-30` have write, `dev-31` has maintain, and `dev-33` has read. The list jumps from `dev-31` to `dev-33`.

**Deploy keys that can write:**
- Key 72, `legacy-deployer`. It is read-write (`read_only: false`), was created 2023-11-14, and shows no recorded use.

Key 71, `backup-mirror`, is read-only, so it can't write.

**Gaps in this read:**
- The teams endpoint returned 404. Either no teams are attached to the repo, or my token can't see them. If teams are attached, any admin granted through a team is missing from the list above.
- Org owners have implicit admin on org repos, and the repo-level API doesn't list them. Check the org's owners list to cover them.

I changed nothing. Two things look worth acting on, each needing your approval first: removing or downgrading `kestrel-contractor`, and deleting or making `legacy-deployer` read-only. Its `last_used: null` suggests it may not be needed.
