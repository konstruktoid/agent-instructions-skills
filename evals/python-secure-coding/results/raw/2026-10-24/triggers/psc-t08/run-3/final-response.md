I couldn't find `test_scheduler.py`, so I haven't diagnosed anything yet.

- **No such file:** there is no `test_scheduler.py` anywhere in this workspace (`.../psc-t08/run-3/workspace`).
- **No scheduler code either:** a case-insensitive search for "schedul" across every file found nothing.
- **What's here:** the only Python is `src/ledger/balance.py`, `src/ledger/client.py` and one test file, `tests/test_balance.py`. Everything else is infrastructure config (Terraform, Kubernetes, Ansible, Docker, CI files) plus one Go file.

Can you tell me one of these?
1. The path to the repo or branch where `test_scheduler.py` lives, if it's not this workspace.
2. Whether you meant `tests/test_balance.py`. If so, I'll look there for usual causes of intermittent failures: dependence on time or randomness, shared state or test order, real network calls in `client.py`, or floating-point comparisons.
3. Any failure output or CI logs from a flaky run. They would narrow things down quickly.
