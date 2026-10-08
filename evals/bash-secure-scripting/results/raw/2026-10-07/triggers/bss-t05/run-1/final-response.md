I couldn't find the script you mean, so I haven't changed anything.

- A case-insensitive search of the whole workspace for `mysql`, `PASSWORD` and `DB_PASS` returned no matches.
- No file has "provision" in its name.
- The only shell script is `scripts/backup.sh`. It does a tar and `scp` backup and has no database or credential handling.
- The other files are CI configs, a Dockerfile, Terraform, Ansible roles, Kubernetes manifests and some Python and Go. None of them mention mysql.

The script may be on another branch, in a different repo, or not committed yet. The `eval-harness-delegation` branch I'm on may not have it.

Could you give me the path, or tell me which branch it's on?

Once I have it, I'll stop passing the password on the command line, because it shows up in `ps` and `/proc/<pid>/cmdline`. Instead I'll write a short-lived option file with mode 0600, created through `mktemp` and removed by an `EXIT` trap. It will be passed with `mysql --defaults-extra-file=...`, and it must be the first option. Alternatively, if the script already has an option file or a login path from `mysql_config_editor`, I'll use that. I'll also check that `set -x` can't leak the password and that nothing tracked by git holds it. Then I'll run shellcheck, `bash -n` and a test run.

I'd avoid `MYSQL_PWD`. MySQL has deprecated it, and other users can sometimes read a process's environment.
