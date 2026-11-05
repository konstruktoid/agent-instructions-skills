Nothing was changed; every call was a read.

**Admins on northwind/ingest** (direct and inherited collaborators, all pages read)
- `maria-lind`
- `kestrel-contractor`: an admin with a contractor-style login. Confirm this grant is still needed.

The full collaborator list is 34 people: 2 admin, 1 maintain, 30 write and 1 read.

**Deploy keys that can write**
- Key 72, `legacy-deployer`: read-write, created 2023-11-14. It is the only writable key.
- Key 71, `backup-mirror`, is read-only, so it is not a concern.

**Gaps in what I could read**
- The teams endpoint returned 404, so I can't say whether any team holds admin. This may be because the repo has no teams or because my token lacks access. If a team has admin, its members are not in the list above.
- The org admins endpoint also returned 404. Org owners have implicit admin on every repo and aren't shown here.
- Treat the list as the admins visible to my token, not a complete list of everyone with admin rights.

**Suggested follow-ups** (I haven't done any of these)
- Check whether `legacy-deployer` is still used. If it is, make it read-only or replace it with a workflow that authenticates with OIDC.
- Confirm that `kestrel-contractor` needs admin. If not, reduce the role to the minimum needed.
