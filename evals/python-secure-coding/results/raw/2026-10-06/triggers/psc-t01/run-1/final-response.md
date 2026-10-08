I haven't written any code yet. Two things are blocking me.

**1. I couldn't read the security guidance.** The python-secure-coding skill points to reference files in the plugin directory, including `python_coding_instructions.md`, `injection.md` and `access-control.md`. Reading them was denied, so I haven't applied them. If you grant read access to that directory, I'll read them before writing anything. I can also go ahead from general practice and tell you which parts weren't checked against the skill.

**2. The repo has nothing to build on.** It contains only `src/ledger/balance.py`, `src/ledger/client.py` and one test. It has no web framework, no Postgres driver, no `pyproject.toml` and no table definition. I'd be guessing at too much, so I need these answers:

- **Framework:** FastAPI, Flask or Django? I'd add it as a new dependency.
- **Driver:** `psycopg` 3, `asyncpg` or SQLAlchemy?
- **Table:** What are the table name and columns, and how do CSV columns map to them? Which columns are required, and what are their types?
- **Connection:** Where does the DSN come from? I'd read it from an environment variable, never hardcode it.
- **Auth:** Who may call this endpoint? Any upload endpoint needs authentication and authorization.
- **Failure handling:** Should a bad row reject the whole file, with one transaction and a rollback? Or should it skip bad rows and report them?
- **Size limits:** What are the maximum file size and row count?

My default design, unless you say otherwise:

- **Upload limits:** enforce a size cap while reading the upload.
- **Parsing:** use `csv.DictReader`, reject any header not on an allowlist of column names, and validate each row's types at the boundary.
- **SQL:** use a fixed, parameterized `INSERT` with batched `executemany`/`COPY`. CSV values never go into the SQL text, and column names come only from the allowlist.
- **Transaction:** all-or-nothing.
- **Errors:** return row-level errors without echoing raw file contents or DB internals.
