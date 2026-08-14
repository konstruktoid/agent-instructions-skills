There's no provisioning script in this repo that puts a database password on the mysql command line — the only shell script present is `scripts/backup.sh`, which does SCP/tar backups and doesn't touch mysql or credentials at all, and nothing else (Ansible roles, Terraform, CI configs) references a DB password either.

Could you point me to the actual file (or paste the relevant snippet)? I don't want to guess at a script that isn't in this workspace.
