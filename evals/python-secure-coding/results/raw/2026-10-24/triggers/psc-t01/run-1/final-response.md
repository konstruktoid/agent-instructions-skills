I haven't written anything yet. Nothing in this repo covers what the endpoint needs, so I'd be guessing at the important parts:

- **No web app.** `src/ledger/` has just two small modules, `balance.py` and `client.py`. There's no Flask, FastAPI or Django app to add a route to.
- **No Postgres code.** There's no driver, connection setup, models or migrations, so I don't know which table "our Postgres table" means or what its columns are.
- **No Python project config.** There's no `pyproject.toml`, so there's no ruff, ty or uv setup to check the change against.
- **The README calls this a "probe-sandbox".** It says it's a mixed demo repo used for trigger evals, not a real service.

To build it properly, I need:

1. **The framework:** FastAPI, Flask, Django, or something else. If you don't mind, I'd suggest FastAPI.
2. **The table:** its name, columns and types, and which CSV header maps to which column.
3. **The database driver:** psycopg 3, SQLAlchemy, asyncpg, or whatever you already use, plus how the connection string is supplied (I'd assume an environment variable).
4. **Who can call it:** what authentication or authorization should protect it.
5. **What happens when a row is bad:** reject the whole file in one transaction, or skip bad rows and report them.

Once I have those, here's how I'd build it:

- **SQL:** a fixed list of allowed columns and parameterized inserts only. Column names from the CSV header never go into the SQL text.
- **Limits:** a cap on upload size and row count, a check that the file is UTF-8, and a check that the header exactly matches the expected columns.
- **Row checks:** each row is validated and converted to the right type before insert, and cells starting with `=`, `+`, `-` or `@` are flagged if the data might be exported to a spreadsheet later.
- **Writes:** rows go in as a batch (`executemany` or `COPY`) inside one transaction.
- **Errors and secrets:** errors come back with row numbers but without raw database messages or the connection string, and credentials are never logged.
- **Checks:** a `pyproject.toml` with ruff and ty, plus tests, all run with `uv run` before I call it done.

If you'd rather have a self-contained example now, say so and I'll write one with a placeholder table. The table definition is the part you'd need to replace.
