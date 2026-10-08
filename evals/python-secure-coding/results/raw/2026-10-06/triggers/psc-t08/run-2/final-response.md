I couldn't find `test_scheduler.py`, so I haven't diagnosed anything yet. The workspace has no file with that name, no other file matching `*sched*.py`, and no file that mentions "scheduler" at all.

The only Python in the repo is `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`. The rest is infra and CI config (Dockerfile, k8s, Terraform, Ansible roles, a Go parser, and so on).

Possible explanations:
- The test lives on another branch or in a different checkout. I'm on `eval-harness-delegation`.
- The file is untracked or gitignored and isn't in this working directory.
- You meant a different file. `tests/test_balance.py` is the only test here.

Can you tell me where `test_scheduler.py` is, or which branch has it? A failure log or traceback from a flaky run would also help. If you meant `test_balance.py`, I can look at that one instead.
