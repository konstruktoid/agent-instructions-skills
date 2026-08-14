I checked the repo and there's no CI job that runs a shell test suite — `.github/workflows/deploy.yml` only echoes the PR title, `.gitlab-ci.yml` runs `npm`, and the Jenkinsfile runs `make build`. There's no bats/shunit2 setup or shellcheck job anywhere, and `scripts/backup.sh` isn't referenced in any of these pipelines.

Could you point me to the specific workflow (or repo, if this is the wrong one) that runs the shell tests? I don't want to guess and add a caching step to the wrong job.
