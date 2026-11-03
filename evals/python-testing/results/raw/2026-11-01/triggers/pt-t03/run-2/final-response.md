I couldn't find an upload validator in this workspace, so I haven't written any tests.

**What the workspace contains:**
- `src/ledger/balance.py` and `src/ledger/client.py`
- `tests/test_balance.py`
- `inventory.ini`

A case-insensitive search of every file for `upload`, `extension`, `max_size` and `oversize` returned nothing. There's no file-size limit or extension allowlist anywhere I could find.

I didn't want to invent a validator just so there would be something to test. Tests written against made-up behaviour wouldn't protect your real code. Also, my current toolset can only read and search files. I can't write files or run pytest here, so I couldn't add or run tests even with the right target.

**To move forward, could you tell me:**
1. **Where the validator is.** It may be in another repo or branch, or it hasn't been committed yet. A path or the code itself would do.
2. **What it should reject:** the maximum size, which extensions are allowed, and what a rejection looks like (which exception it raises or what it returns).

With that, I'll write the tests to match `tests/test_balance.py`. They'll cover the oversized and bad-extension cases plus the edges: exactly at the limit, one byte over, extension case (`.PNG` vs `.png`), double extensions (`x.png.exe`), no extension, and empty files. Then I'll run the full suite, or give you the files and the command to run if I still can't write here.
