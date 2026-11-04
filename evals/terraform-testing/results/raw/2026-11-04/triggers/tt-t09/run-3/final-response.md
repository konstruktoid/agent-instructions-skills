I couldn't add the test, because this repo has no config loader and nothing that handles a timeout.

- `src/ledger/client.py` only has a `get(transport, path)` retry helper with a fixed `MAX_ATTEMPTS = 3`.
- `src/ledger/balance.py` is the only other source module.
- A search for "timeout" across the repo found nothing.

A test that checks rejection of a negative timeout would have no code to call. To avoid inventing an API, I stopped here.

Which of these do you want?
1. The loader lives elsewhere (another branch or repo). Point me to it and I'll write the test against it.
2. You want me to build a config loader with timeout validation, plus the test. If so, tell me what it should look like: the module name, whether it reads a file or env vars or a dict, and whether to raise `ValueError` for a negative timeout.
