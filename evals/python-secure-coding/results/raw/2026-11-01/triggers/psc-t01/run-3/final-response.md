I haven't written any code yet. The repo is missing what I'd need to build this properly:

- **No web framework.** `src/ledger/` has only `balance.py` and `client.py`. There's no Flask, FastAPI or Django app to attach an endpoint to.
- **No Postgres code.** There's no database driver, connection setup or table schema, so I don't know which table "our Postgres table" is or what its columns are.
- **No `pyproject.toml`.** There are no declared dependencies and no lint or type-check config.

I'd rather ask than guess column names that the inserts would then rely on. A few questions:

1. **Framework:** Should I add one? I'd suggest FastAPI. Or does an app already live somewhere else?
2. **Database driver:** psycopg 3, SQLAlchemy, or something you already use?
3. **Table:** What's its name, what are its columns and types, and how should CSV headers map to them?
4. **Bad data:** If one row is invalid, should the whole upload be rejected (one transaction), or should the bad rows be skipped and reported?
5. **Access and limits:** Who can call this endpoint (what login or permission), and what's the largest file or row count to accept?

Here's how I'll build it once I have answers:

- **Safe SQL:** row values are always passed to the database separately from the SQL text, never pasted into it. The table and column names are fixed in the code and never taken from the CSV headers. For large files I'll use batched inserts or `COPY`.
- **Checks on the upload:** a size cap, required UTF-8, an exact match on the expected headers, and type checks on each row before anything is written. Error messages won't repeat back the raw CSV contents.
- **Credentials:** the database connection string comes from an environment variable or secret, not from the code, and it never appears in logs or responses.
- **Checks before calling it done:** `uv run ruff check`, `ruff format --check` and `ty check`, plus a test for the endpoint.

One note: you declined my request to read the skill's `references/injection.md`, so I'm working from the skill's checklist rather than that file. If you want that guidance applied too, allow the read.
