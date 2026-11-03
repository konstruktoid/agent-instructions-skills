I didn't add the endpoint yet. The repo doesn't have what it would plug into, and guessing would mean writing code you'd likely throw away.

**What I found:**
- The only Python is `src/ledger/balance.py` (a `balance()` helper) and `src/ledger/client.py` (a transport retry wrapper). There's no web framework, no HTTP routes and no app entry point.
- Nothing connects to Postgres: no driver, no connection setup, no schema or migrations. So I don't know which table you mean or what columns it has.
- There's no `pyproject.toml` or lockfile, so there's no `uv run ruff` / `ty` setup to check new code against.
- I was blocked from reading the security skill's SQL and input-handling reference file. If you want me to use it, I'll need permission to read it.

**What I need from you:**
1. **Framework:** FastAPI, Flask, Django, or something else? If you don't mind, I'd use FastAPI.
2. **Table:** its name and columns with types, or a migration/DDL file I can read. I'd map CSV headers to an explicit list of allowed columns rather than taking column names from the file.
3. **Database access:** psycopg 3, SQLAlchemy, or asyncpg? And where does the connection string come from? I'd read it from an environment variable, never hard-code it.
4. **Bad rows:** if one row is invalid, should the whole upload fail (one transaction, my default) or should the good rows go in and the bad ones be reported?
5. **Limits and auth:** a maximum file size and row count, and who's allowed to call this endpoint.

**What I'll build once I have those:**
- Every value is passed as a query parameter, never formatted into the SQL string. Table and column names come only from a fixed list in the code.
- The CSV is read as UTF-8 text, with size and row limits applied at the request boundary. Each row is checked against a typed model before anything is inserted.
- Rows are inserted in batches inside a single transaction.
- Errors return row numbers but not raw cell contents or database error messages, and the upload isn't logged in full.
- Tests, plus ruff and ty set up through `uv` so the checks actually run.
