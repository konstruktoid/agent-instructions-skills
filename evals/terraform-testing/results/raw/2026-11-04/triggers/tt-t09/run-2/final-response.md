I searched the repo and found no config loader and no timeout handling. The only source files are `src/ledger/balance.py` and `src/ledger/client.py`. Neither one loads config or mentions "timeout". I didn't add a test, because it would have to call code that doesn't exist.

Which of these do you want?
- **The loader is elsewhere.** Tell me where it is (another branch, package or path), and I'll write the test against it.
- **It doesn't exist yet.** I can add a `load_config` function that raises `ValueError` on a negative timeout, plus the pytest case. For example, `tests/test_config.py` would use `pytest.raises(ValueError)`. I'd need to know the config format (dict, TOML, env vars) and where it should live.
