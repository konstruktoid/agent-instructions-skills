I couldn't add these tests because there's no upload validator in this workspace.

**What's in the repo:**
- `src/ledger/balance.py` and `src/ledger/client.py`, a small ledger package
- `tests/test_balance.py`, which has one plain pytest function test (no conftest or fixtures)
- `inventory.ini`
- No `pyproject.toml`, `pytest.ini`, `setup.cfg` or `tox.ini`

I searched every file for `upload`, `extension`, `max_size` and `oversiz`, case-insensitive, and found nothing. Nothing in the codebase checks file size or file extension, so there's nothing to write rejection-path tests against. I didn't write a test that only guesses at an interface, because it couldn't fail for a real bug.

I also have no file-writing or shell tools in this session. So even once the validator turns up, I can draft the tests here but can't save them to disk or run the suite.

**How to continue (pick one):**
1. **The validator is somewhere else.** Give me the path to the repo or branch where it lives, and I'll read it and match its tests to the style in `tests/test_balance.py`.
2. **It hasn't been written yet.** Tell me the size limit, the allowed extensions and how a rejection should show up (raises a specific exception or returns an error). I'll draft the tests for that, plus the validator if you want it.
3. **It lives in another file type** (a config, or code in another language). Point me to it. pytest only covers Python, so the right test approach may be different.

When I can write the tests, they'll cover rejecting oversized files (one byte over the limit, and exactly at the limit as the boundary that should pass), disallowed extensions, case and double-extension tricks like `.PHP` and `file.jpg.exe`, files with no extension, and empty files.
