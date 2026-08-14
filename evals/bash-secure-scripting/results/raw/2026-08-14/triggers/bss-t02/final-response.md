I searched the repo but couldn't find a script that builds an SSH command from a branch name — there's no `ssh` usage or branch interpolation anywhere in the tree (checked `.github/workflows/deploy.yml`, `Jenkinsfile`, `.gitlab-ci.yml`, `scripts/backup.sh`, and grepped for `ssh`/`branch` repo-wide with no hits).

Could you point me to the actual file (or paste the relevant snippet)? Once I have it I'll review it with the bash-secure-scripting skill, focused on injection risk from the interpolated branch name.
