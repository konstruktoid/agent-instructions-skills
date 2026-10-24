I haven't changed any files, so nothing was linted or tested. There are two reasons:

- **I can't write files in this session.** I only have read and search tools, so the code below is a draft for you to paste in.
- **The repo has nothing to build the endpoint on.** There's no web framework, no database driver, no `pyproject.toml`, and no table schema. The only Postgres in the repo is the `postgres:17` image in `docker-compose.yml`. The Python code is two small modules, `src/ledger/balance.py` and `src/ledger/client.py`.

I also couldn't read the secure-coding skill's reference file on injection (the read permission was declined). The draft follows the same rules anyway.

## Draft (assumes FastAPI and psycopg 3)

I based the columns on the `entry.account` / `entry.amount` fields in `balance.py`. Swap in your real table and columns.

```python
"""HTTP endpoint that imports ledger entries from an uploaded CSV."""

import csv
import io
import os
from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI, HTTPException, UploadFile

app = FastAPI()

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_ROWS = 50_000
MAX_ACCOUNT_LEN = 64
# Fixed set of columns: header names from the upload never reach the SQL text.
EXPECTED_COLUMNS = ("account", "amount")
INSERT_SQL = "INSERT INTO ledger_entries (account, amount) VALUES (%s, %s)"


def require_importer() -> None:
    """Placeholder: replace with your real authentication and authorization check."""
    raise HTTPException(status_code=401)


def parse_rows(text: str) -> list[tuple[str, int]]:
    """Validate the CSV and return typed rows, rejecting the whole file on any bad row."""
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != EXPECTED_COLUMNS:
        raise HTTPException(422, f"header must be exactly: {','.join(EXPECTED_COLUMNS)}")
    rows: list[tuple[str, int]] = []
    for line_no, record in enumerate(reader, start=2):
        if len(rows) >= MAX_ROWS:
            raise HTTPException(413, f"more than {MAX_ROWS} rows")
        if None in record:  # extra fields beyond the header
            raise HTTPException(422, f"line {line_no}: too many fields")
        account = (record["account"] or "").strip()
        if not account or len(account) > MAX_ACCOUNT_LEN:
            raise HTTPException(422, f"line {line_no}: invalid account")
        try:
            amount = int(record["amount"] or "")
        except ValueError:
            raise HTTPException(422, f"line {line_no}: amount must be an integer") from None
        rows.append((account, amount))
    return rows


@app.post("/ledger/import", status_code=201)
async def import_ledger_csv(
    file: UploadFile, _auth: Annotated[None, Depends(require_importer)]
) -> dict[str, int]:
    """Insert every row of an uploaded CSV into ledger_entries in one transaction."""
    raw = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "file too large")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(422, "file must be UTF-8") from None
    try:
        rows = parse_rows(text)
    except csv.Error:
        raise HTTPException(422, "malformed CSV") from None

    # DSN comes from the environment, never from source; errors are not echoed to the client.
    try:
        async with await psycopg.AsyncConnection.connect(os.environ["DATABASE_URL"]) as conn:
            async with conn.cursor() as cur:
                await cur.executemany(INSERT_SQL, rows)
    except psycopg.Error:
        raise HTTPException(500, "import failed") from None
    return {"inserted": len(rows)}
```

## Security decisions in the draft

- **SQL injection:** every value goes in as a query parameter (`%s` with `executemany`). The table and column names are fixed in the code, and the uploaded header is only checked against them, never put into the SQL.
- **Resource limits:** the upload is capped at a set size and row count, and the server never reads more than the cap plus one byte.
- **Validation:** rows are checked and typed before touching the database. One bad row rejects the whole file, and the insert is a single transaction, so a partial import can't happen.
- **Auth:** `require_importer` rejects every request until you replace it with your real check. That way it can't ship open by accident.
- **Errors and secrets:** database errors aren't sent back to the caller (`from None`), and the connection string comes from `DATABASE_URL`, not the code.

## What I need from you

1. **Framework:** is it FastAPI or something else? Should this go in a new module, e.g. `src/ledger/api.py`?
2. **Table:** the real table name, its columns and their types.
3. **Auth:** how callers are authenticated and who is allowed to import.
4. **Large files:** for very large uploads, should I switch to Postgres `COPY` (`cur.copy(...)`, still fed with validated values)? It's much faster than row-by-row inserts.

If you turn on file editing, I'll add the module and tests, add the dependencies to the project, and run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`.
