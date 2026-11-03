I didn't add any tests, because I couldn't find an upload validator in this repository.

The workspace contains only these files:

- `src/ledger/balance.py` and `src/ledger/client.py`
- `tests/test_balance.py` (one pytest test)
- `inventory.ini`

I searched the whole workspace for `upload`, `extension`, `max_size`, `too large` and `oversiz`, and nothing matched. There's no code that checks file size or extensions, so there's nothing for the oversized or bad-extension tests to run against. Separately, I don't have file-writing or shell tools in this session, so I couldn't have created or run test files here either way.

To move forward, I need one of these:

1. **The validator lives somewhere else** (another repo, branch or directory): point me to it and I'll write the tests next to it, following that project's test style.
2. **It hasn't been written yet:** tell me the rules (size limit, allowed extensions, whether it raises an error or returns a result) and I can draft the validator and its rejection tests. They would go in `tests/` with the same plain-function style as `tests/test_balance.py`.

Once there's code and a session with write access, the tests would cover at least:

- **Oversized:** a file exactly at the limit is accepted, and one byte over is rejected.
- **Bad extension:** a disallowed extension is rejected, plus uppercase variants (`.PHP`), double extensions (`shell.php.jpg`, `image.jpg.php`), no extension, and a trailing dot.
- **Other rejections:** an empty file, if the rules forbid it, and path-traversal names (`../x.png`) if the validator handles filenames.
