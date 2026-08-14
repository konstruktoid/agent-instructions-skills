I looked through the repo and don't find a CI job that runs a shell test suite:

- `.github/workflows/deploy.yml` just echoes the PR title on `pull_request` — no test step at all.
- `.gitlab-ci.yml` only has a Node `build` stage (`npm ci && npm run build`) — no shell/bash test stage.
- There's no bats/shunit2 setup, and the only test file in the repo is `tests/test_balance.py` (Python). The only shell script is `scripts/backup.sh`, with no associated test suite.

So there's nothing to add caching to yet — could you point me at the actual workflow/job you mean, or is this describing work that hasn't been added to this repo yet?
