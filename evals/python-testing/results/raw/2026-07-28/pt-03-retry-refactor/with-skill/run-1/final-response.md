All 6 tests pass and formatting is clean.

**Summary:** Extracted the duplicated retry loop from `Client.get` and `Client.head` into `Client._with_retries(method, path)` in `src/fetcher/client.py`. Both public methods now delegate to it, preserving identical attempt counting and exception-on-exhaustion behavior. Added `test_head_retries_until_it_succeeds` and `test_head_gives_up_after_the_attempt_limit` in `tests/test_client.py`, mirroring the existing `get` tests, since `head` previously had no retry/exhaustion coverage of its own even though it shared the same logic.

Verified: `pytest` (6/6 pass), `ruff format --check` (clean). Two pre-existing issues were checked and confirmed unrelated to this change (reproduced identically on unmodified `main`): a `ruff check` import-sort warning in the test file's original import block, and `ty check` environment-resolution errors caused by the outer monorepo layout — neither introduced by this refactor.
