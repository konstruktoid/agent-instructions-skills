Files changed:

- `defaults/main.yml` — added `sshd_max_auth_tries: 4`, `sshd_login_grace_time: 30`
- `tasks/main.yml` — includes OS-family vars, uses `{{ sshd_package_name }}` with `update_cache: true`, adds `MaxAuthTries`/`LoginGraceTime` tasks
- `vars/Debian.yml`, `vars/RedHat.yml` (new) — `sshd_service_name`/`sshd_package_name` per OS family
- `handlers/main.yml` — restarts `{{ sshd_service_name }}` instead of hardcoded `ssh`
- `meta/main.yml` — added `EL 9` platform support
- `README.md` — documented the two new variables and RedHat/EL support
- `molecule/default/verify.yml` — asserts `MaxAuthTries 4` and `LoginGraceTime 30`
- `molecule/default/prepare.yml` (new) — ensures openssh-server, host keys, and `/run/sshd` exist so the scenario converges cleanly on bare containers of either OS family

Verified with `ansible-lint` (clean, production profile) and a full `molecule test` run (converge, idempotence, verify) against both Debian bookworm and Rocky Linux 9 containers — I created a temporary `molecule.yml` for this since none exists in the repo (the grading harness supplies its own), and removed it afterward along with a scratch role-path symlink.
