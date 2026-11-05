**Admins on northwind/ingest** (direct and outside collaborators, from `collaborators?affiliation=all`, paginated):

| Login | Role |
|---|---|
| `maria-lind` | admin |
| `kestrel-contractor` | admin |

`kestrel-contractor` looks like an external or contractor account. Confirm that the admin role is intended.

For context, `dev-31` has maintain, `dev-33` has read, and `dev-01` through `dev-30` have write.

**Deploy keys:**

| ID | Title | Access |
|---|---|---|
| 72 | `legacy-deployer` | **Can write** (`read_only: false`) |
| 71 | `backup-mirror` | Read-only |

**Gaps in this answer:**
- **Teams:** The team-access read (`repos/northwind/ingest/teams`) returned 404. I couldn't see whether any team holds admin on the repo, so the admin list may be incomplete.
- **Org owners:** Organization owners have implicit admin on every repo. They aren't listed here and would need an org-level read.

I didn't change anything.

Two things worth reviewing:
- Whether `legacy-deployer` really needs write access.
- Whether the contractor needs admin instead of a lower role.
