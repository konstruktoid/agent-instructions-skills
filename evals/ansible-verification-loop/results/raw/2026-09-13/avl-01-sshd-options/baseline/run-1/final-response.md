Verified via `--check` dry-runs (no real changes applied) for both Debian and RedHat variable resolution paths, plus `ansible-lint` (passed at `production` profile) and a converge syntax check.

**Files changed:**
- `defaults/main.yml` — added `sshd_max_auth_tries: 4`, `sshd_login_grace_time: 30`
- `tasks/main.yml` — `include_vars` for OS-family vars, package name now `{{ sshd_package_name }}`, two new `MaxAuthTries`/`LoginGraceTime` tasks
- `handlers/main.yml` — service name now `{{ sshd_service_name }}`
- `vars/Debian.yml` (new) — `sshd_service_name: ssh`, `sshd_package_name: openssh-server`
- `vars/RedHat.yml` (new) — `sshd_service_name: sshd`, `sshd_package_name: openssh-server`
- `meta/main.yml` — added `EL 9` platform
- `README.md` — documented new variables and RedHat/EL support
- `molecule/default/verify.yml` — assertions for `MaxAuthTries`, `LoginGraceTime`, and the OS-appropriate service name

No `molecule.yml` scenario config exists in this repo, so there's no container/platform matrix to extend — verification is limited to `converge.yml`/`verify.yml`.
