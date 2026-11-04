I can't write this test yet, because the repo has no config loader and no timeout setting.

- `src/ledger/client.py` only has `get(transport, path)`, which retries up to `MAX_ATTEMPTS = 3` times. It has no timeout.
- `src/ledger/balance.py` is a balance helper.
- A search for "timeout" across the repo found nothing.
- The only existing test is `tests/test_balance.py`.

A test for "rejects a negative timeout" would have nothing to call. Do you want me to do one of these?

1. **Write the loader too.** I'd add something like `src/ledger/config.py` with `load_config(...)` that raises `ValueError` when `timeout < 0`, plus the pytest case. Tell me where the config comes from (dict, JSON/TOML file, env vars) and what the default timeout should be.
2. **Test a loader that lives elsewhere.** Point me to the branch or file that has it.
