I didn't write any tests, because I couldn't find an upload validator in this repo.

The workspace only has `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`. Searching all files for "upload", "valid", "extension" and "size" returned no matches. The branch may be the wrong one, or the validator may live in another repo or an uncommitted file.

Tests written against a validator I can't see would mean guessing its function name, its signature, how it signals rejection (exception or return value), the size limit, and the allowed extensions. They would probably fail, or pass for the wrong reasons.

Can you tell me one of these?
- The path to the validator, or the branch it's on.
- If it doesn't exist yet, the intended interface: the function name, the size limit, the allowed extensions, and whether rejection raises or returns an error.

Once I have that, I'll read `tests/test_balance.py` to match its conventions. Then I'll add tests for the oversized, bad-extension and other rejection paths, and run the suite.
