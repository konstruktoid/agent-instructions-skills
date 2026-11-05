I couldn't add the test, because this repo has no config loader.

The only Python files are `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`. Nothing in them parses config, and nothing mentions "timeout". `client.py` only retries a transport call a fixed 3 times. A search for `timeout` across the workspace found no matches.

A test written now would have to invent the loader's name, its import path and the exception it raises on a negative timeout. That would be a made-up test, not a check on your code.

Could you tell me one of these?
- **Where the loader lives:** it may be on another branch or in a different directory.
- **What you want built:** if the loader doesn't exist yet, I can write it with a negative-timeout check and the pytest case together. I'd need the config format (dict, YAML, env vars) and the exception type you want.
