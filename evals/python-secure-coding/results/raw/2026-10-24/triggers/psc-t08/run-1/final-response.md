I couldn't find `test_scheduler.py` in this repository, so I haven't been able to look into the flaky test.

What I checked in the workspace:
- **Python files:** there are only three: `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`.
- **Text search:** searching every file for "schedul" (case-insensitive) found nothing. No code, config or CI file mentions a scheduler.
- **Other files:** the rest of the repo is infrastructure and CI config (Go parser, Terraform, Docker, k8s, Ansible nginx role, Jenkins, GitLab and GitHub workflows, a backup script).

Possible reasons:
1. The test lives in another repo or on a branch that isn't checked out here (this is `main`).
2. The file was renamed. If you meant `tests/test_balance.py`, I can look into that one instead.
3. The test is generated or fetched at CI time. I didn't see anything that does this, but I didn't read every CI file.

Could you point me to the right repo, branch or path? If you have a failing CI log or traceback, paste it in. That usually shows the cause fastest, whether it's test ordering, shared state, timing or sleeps, unseeded randomness, or the real clock or timezone.
