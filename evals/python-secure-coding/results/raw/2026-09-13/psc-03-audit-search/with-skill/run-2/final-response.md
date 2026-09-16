Everything works as expected and the checks pass (no leftover `audit.db` created since the temp DB path was overridden; also removed the `/tmp` test DB). No test suite exists in this repo beyond ruff/format/ty, all of which are clean.

**Files changed:**
- `src/auditlog/filters.py` — replaced `quote_literal` with allowlist validation in `order_clause` (fixes an unvalidated `ORDER BY` injection point in `--sort`/`--direction`)
- `src/auditlog/search.py` — parameterized the query, made `action` optional, added `--since`, `--limit`, `--offset` with validation
- `README.md` — documented the new/changed flags

Deviation from a literal reading of the task: I dropped `quote_literal`'s string-concatenation approach for bound parameters, per the repo's own security-coding guidance on never building SQL by hand-escaping values — the old code was also exploitable via `--sort`/`--direction` since those were interpolated with no validation at all.
