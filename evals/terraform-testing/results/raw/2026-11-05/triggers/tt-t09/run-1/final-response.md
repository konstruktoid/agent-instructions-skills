I can't add this test yet, because the repo has no config loader to test. I searched the Python files for "timeout", "config" and "load" and found nothing. The only modules are:

- `src/ledger/balance.py`
- `src/ledger/client.py`, a retry wrapper with no timeout or config handling
- `tests/test_balance.py`, the only existing test

The only "config" match in the repo is `roles/nginx/tasks/main.yml`, which is unrelated.

A test written now would have to invent a `load_config` function and a `ConfigError` that don't exist. It would fail on import and tell you nothing.

Which of these is the case?
1. The loader is on another branch or in another repo. If so, tell me where.
2. You want me to write the loader as well, as `src/ledger/config.py` with a `load_config` that raises `ValueError` on a negative `timeout`, plus the test.
3. The timeout check belongs somewhere else, such as `client.get`.

If it's option 2, tell me the config format (dict, JSON, TOML, env vars) and the exception type you want.
