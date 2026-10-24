I haven't added the endpoint yet. A few things are missing, and I can't edit files or run commands in this session anyway.

**What I found:** the only Python code in the repo is `src/ledger/balance.py` and `src/ledger/client.py`. There's no web framework, no Postgres connection code, no table schema and no `pyproject.toml`. That means I don't know which framework to use, which table to write to, or what its columns are. I also tried to read the secure-coding skill's injection guidance and that read was denied, so what follows is written without it.

Here's a draft you can adapt. It assumes FastAPI and psycopg 3, and uses a placeholder `ledger_entries(account, amount)` table that you should replace with yours:

```python
"""HTTP endpoint that imports ledger entries from an uploaded CSV."""

import csv
import io
import os

import psycopg
from fastapi import Depends, FastAPI, HTTPException, UploadFile

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_ROWS = 50_000
# Allowlist: CSV headers must match exactly; never take column names from the file.
COLUMNS = ("account", "amount")
INSERT_SQL = "INSERT INTO ledger_entries (account, amount) VALUES (%s, %s)"

app = FastAPI()


def require_importer() -> None:
    """Placeholder for your real authn/authz check; must fail closed."""
    raise HTTPException(status_code=401)


def parse_rows(raw: bytes) -> list[tuple[str, int]]:
    """Validate the CSV at the boundary and return typed rows."""
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != COLUMNS:
        raise HTTPException(status_code=400, detail=f"Expected header: {','.join(COLUMNS)}")
    rows: list[tuple[str, int]] = []
    for line_no, record in enumerate(reader, start=2):
        if len(rows) >= MAX_ROWS:
            raise HTTPException(status_code=413, detail="Too many rows")
        account = (record["account"] or "").strip()
        if not account or len(account) > 64:
            raise HTTPException(status_code=400, detail=f"Line {line_no}: invalid account")
        try:
            amount = int(record["amount"])
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=f"Line {line_no}: invalid amount") from exc
        rows.append((account, amount))
    return rows


@app.post("/imports/ledger-entries", dependencies=[Depends(require_importer)])
async def import_ledger_entries(file: UploadFile) -> dict[str, int]:
    """Insert every CSV row in one transaction; all rows or none."""
    raw = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    rows = parse_rows(raw)
    async with await psycopg.AsyncConnection.connect(os.environ["DATABASE_URL"]) as conn:
        async with conn.cursor() as cur:
            await cur.executemany(INSERT_SQL, rows)
    return {"inserted": len(rows)}
```

**Security choices in the draft:**
- **SQL injection:** values are passed as query parameters, never formatted into the SQL string. Column names are fixed in code, and the CSV header has to match them exactly.
- **Input limits:** the upload size and row count are capped, the file must be UTF-8, and each field is checked and converted to its type before anything touches the database.
- **All-or-nothing:** every row goes in one transaction, so a bad row can't leave a half-finished import.
- **Credentials:** the database connection string comes from the environment and isn't hardcoded or logged.
- **Access control:** the `require_importer` placeholder rejects every request until you connect it to your real auth check.

**To finish this I need:**
1. Which web framework and database driver you use, or are these going in new?
2. The real table name and columns, and what should happen to duplicates (reject, skip or update).
3. Where the code should go, and how auth works in your app.

Once you answer and file writes are allowed, I'll add the endpoint and tests, then run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`. None of those have been run on this draft.
