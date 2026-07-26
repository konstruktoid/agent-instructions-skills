There's no pagination helper anywhere in this workspace — the repo contains `src/ledger/balance.py` and `src/ledger/client.py` (a retry helper), plus infra/config files (Terraform, Ansible, Docker, CI, Go). No file mentions pagination, `page`, `offset`, or `limit`, and there's no git history here to check for a recent fix either (no `.git` in the workspace).

Could you point me to the file with the pagination helper, or confirm which repo/branch it's in? I don't want to guess and write a test against the wrong code.
