I checked this repo's workflows (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`) and CI configs (`Jenkinsfile`) — none of them run a shell/bash test suite, and there's no `bats`/`shunit2`/shellcheck setup anywhere in the repo. There's nothing here matching "the CI job that runs our shell test suite."

Could you point me to the workflow file you mean, or is it possible this is a different repo/branch than what's currently checked out?
