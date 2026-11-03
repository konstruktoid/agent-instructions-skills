I haven't written any code yet. The repo is missing a few things I'd otherwise have to invent:

- **No web app.** The only Python is `src/ledger/` (`balance.py` and `client.py`). There's no FastAPI, Flask or Django, so there's nothing to add an endpoint to.
- **No table definition.** `docker-compose.yml` starts a `postgres:17` container, but there's no `CREATE TABLE`, migration or model anywhere. I don't know the table's name, columns or types.
- **No Postgres driver or `pyproject.toml`.** I'd need to add dependencies such as `psycopg` and a web framework, and there's no project file to pin them in or to run `ruff`/`ty` from.

To write it, I need:

1. **Framework:** FastAPI, Flask, or something else?
2. **Table:** its name and columns (or the DDL), and which CSV header maps to which column.
3. **Connection:** where the database credentials come from (I'll assume a `DATABASE_URL` environment variable unless you say otherwise).
4. **Bad rows:** should one bad row reject the whole upload (one transaction, all or nothing), or should the good rows go in and the bad ones be reported?

Once I have those, here's the plan. These are the security and correctness choices I'd make by default:

- **No SQL injection:** row values are passed as query parameters, never formatted into the SQL string. The table and column names are fixed in the code; nothing from the CSV header ends up in the SQL.
- **Checks on the upload:** a size limit, a maximum row count, UTF-8 decoding, and the CSV header must exactly match the expected columns. Each row is converted to the right types before it's inserted, and errors give the row number but don't echo the row's contents back.
- **Batched inserts:** rows go in with `executemany` or `COPY` inside one transaction, not one round trip per row.
- **Access control:** the endpoint requires authentication, so I need to know what your existing auth is.
- **Credentials:** read from the environment, never hardcoded or logged.
- **Verification:** tests for a valid file, a wrong header, a file over the limit and a bad value, then `uv run ruff check`, `ruff format --check` and `ty check` until they're clean.
