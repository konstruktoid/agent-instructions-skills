I haven't written any code yet, because the repo doesn't have what this endpoint needs, and I'd be guessing at several things.

- **No web framework or database layer.** `src/ledger/` has only `balance.py` and `client.py`. There's no `pyproject.toml`, no dependency list, and no existing Postgres code. The only Postgres reference is `image: postgres:17` in `docker-compose.yml`.
- **Your real service may live elsewhere.** If so, tell me where, and I'll add the endpoint to it.
- **I couldn't read the secure-coding references.** The permission request for the skill's instruction and reference files was denied. I'll apply the usual practices from general knowledge, but I haven't checked them against those files.

Questions:
1. **Framework:** FastAPI, Flask, Django, or something else? If it's none of these, I'd default to FastAPI.
2. **Driver:** `psycopg` 3, asyncpg, or SQLAlchemy? Adding any of these is a new dependency, and I'd need `pyproject.toml` set up for `uv`.
3. **Table:** What are its name and columns, and which CSV headers map to which columns? Is it an insert or an upsert, and on which key?
4. **Connection:** How do you supply credentials? I'd read a `DATABASE_URL` environment variable and never hardcode it.
5. **Access control:** Who may call this endpoint, and what auth already exists?

Unless you say otherwise, the design I'd build is:
- Cap the upload size and require a CSV content type.
- Check the header row against a fixed allowlist of columns and validate each row's types.
- Insert with parameterized queries only. Table and column names would come from constants, never from the CSV.
- Insert in batches inside a single transaction, so a bad row rolls back the whole upload.
- Return generic errors that don't echo row contents.
