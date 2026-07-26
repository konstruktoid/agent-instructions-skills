All files parse and lint cleanly. Summary of changes:

- **`defaults/main.yml`**: added `sshd_max_auth_tries: 4` and `sshd_login_grace_time: 30`.
- **`vars/Debian.yml`** / **`vars/RedHat.yml`** (new): OS-specific `sshd_service_name` (`ssh` vs `sshd`) and `sshd_package_name` (`openssh-server` on both, now sourced per-family).
- **`tasks/main.yml`**: loads the OS-specific vars file first, installs `{{ sshd_package_name }}`, and adds two new `lineinfile` tasks for `MaxAuthTries` and `LoginGraceTime`, following the same pattern (regexp, `validate`, `mode: "0600"`, notify handler) as the existing options.
- **`handlers/main.yml`**: restarts `{{ sshd_service_name }}` instead of the hardcoded `ssh`.
- **`meta/main.yml`**: added `EL` (RedHat family) platform support alongside Debian.
- **`README.md`**: documented the two new variables and RedHat/EL support, noting the service-name difference.
- **`molecule/default/verify.yml`**: asserts `MaxAuthTries 4` and `LoginGraceTime 30` are present, and checks the correct service (`ssh.service` vs `sshd.service`) is running based on `os_family`.

Existing Debian behavior is unchanged (same package/service names), so nothing there should break.
