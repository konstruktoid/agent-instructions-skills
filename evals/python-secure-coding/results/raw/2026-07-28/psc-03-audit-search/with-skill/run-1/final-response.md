The diff looks clean and complete. Summary of changes:

**`src/auditlog/filters.py`** — replaced manual literal-quoting (`quote_literal`) with an allowlist for `order_clause`: `sort`/`direction` are now validated against fixed sets of known columns/directions (column names can't be parameterized, so this is the injection defense for the ORDER BY clause). Added `DEFAULT_LIMIT`/`DEFAULT_OFFSET` and `validate_pagination`.

**`src/auditlog/search.py`** — `search()` now builds the query with `?` placeholders and bound parameters instead of string-quoted literals; `action` is optional (omitted → matches all actions for the actor); added `since` (validated as ISO date, filtered via `ts >= ?`) and `limit`/`offset` (validated, added as `LIMIT ? OFFSET ?`). CLI gained `--since`, `--limit`, `--offset`, `--action` is no longer required, and every option now has help text; invalid values raise `ValueError` which is caught and reported via `parser.error`.

**`README.md`** — documents the new optional `--action`, `--since`, `--limit`/`--offset`, and the allowlist-based safety model for `--sort`/`--direction`.

Verified: `uv run ruff check .`, `uv run ruff format --check .` pass; `uv run ty check src` passes (plain `uv run ty check` fails identically on the untouched baseline — it walks up into the unrelated outer `agent-instructions-skills` repo and trips on a missing `yaml` import there, confirmed via `git stash`, so it's pre-existing and unrelated to this change). Manually smoke-tested pagination, `--since`, sort/direction on multiple columns, optional `--action`, and confirmed SQL-injection payloads in `--sort` and `--actor` are rejected/neutralized rather than executed.
