I couldn't find a provisioning script or any `mysql` call in this workspace, so I haven't changed anything.

I searched every file for `mysql`, `PASSWORD` and `DB_PASS`, case-insensitively, and got no matches. The only shell script is `scripts/backup.sh`, which backs up `/srv/ledger/data` and copies it over `scp`. It has no database access and no password. The other files are CI configs, a Dockerfile, `docker-compose.yml`, Terraform, Ansible roles, a Kubernetes manifest and some Python and Go. None of them mention mysql.

Where is the provisioning script? It may be on another branch, in another directory, or not committed yet. If you give me the path, I'll fix it.

The usual fix is to stop passing the password as an argument, because that exposes it in `ps` and `/proc`. Instead, the script would write a temporary option file with `mktemp` and mode 0600, with an `EXIT` trap that removes it. It would then run `mysql --defaults-extra-file=...`. `MYSQL_PWD` is an alternative, but it is weaker. I'd also add `set -Eeuo pipefail` and make sure no `set -x` covers the credential.

Separately, `scripts/backup.sh` has problems of its own:
- It has no strict mode.
- Its variables are unquoted.
- It uses a predictable `/tmp/backup.$$` instead of `mktemp`.
- Its cleanup runs only if every earlier step succeeds.

I can fix those too if you want.
