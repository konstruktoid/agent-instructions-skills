I couldn't add the test because there's no config loader in this repo to test.

- **Python source:** `src/ledger/` has only `balance.py` and `client.py`. `client.py` is a retry wrapper around a transport call.
- **Timeouts:** no Python file mentions a timeout.
- **Config loading:** the only "config" hit is `roles/nginx/tasks/main.yml`, an Ansible file.
- **Tests:** `tests/test_balance.py` is the only test file.

A test for rejecting a negative timeout would have nothing to import. It would also fail, or pass vacuously, if I invented a loader.

Which of these is the case?
1. The loader is on another branch or in another repo. Tell me where and I'll write the test there.
2. The loader doesn't exist yet. I can write the loader, with validation that rejects `timeout < 0`, and the test together. I'd need to know the config format (YAML, TOML, env vars or something else) and where it should live.
3. You meant the Terraform side (a variable `validation` block). If so, the test would be a `terraform test` `expect_failures` case. I don't see any `.tf` files here either, so I'd need the module path.
