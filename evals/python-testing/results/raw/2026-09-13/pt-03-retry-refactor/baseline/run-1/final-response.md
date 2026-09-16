All 4 tests pass, ruff is clean.

Changed files:
- `src/fetcher/client.py` — extracted `_with_retries(method, path)`, `get`/`head` now delegate to it; loop, attempt counting, and exception behavior on exhaustion are unchanged.
- `tests/test_client.py` — ran `ruff --fix` to sort a pre-existing unsorted import block (unrelated to the refactor, confirmed present before my change).

`ty check` fails, but identically on the pre-refactor code: it treats the outer `agent-instructions-skills` repo as project root (due to this workspace being nested under `evals/*/results`, which only partially matches that repo's `tool.ty.src` exclude glob) and reports errors in unrelated scripts, plus `fetcher` import resolution failures caused by no editable install / src-layout hint — none of it touches `client.py`. Not something this task should fix.

Task complete — recommend `/clear` before starting anything unrelated.
