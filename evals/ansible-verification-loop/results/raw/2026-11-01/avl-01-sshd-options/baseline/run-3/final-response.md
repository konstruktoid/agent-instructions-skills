I added `MaxAuthTries` and `LoginGraceTime` and RedHat support. Lint and a syntax check pass, but I haven't run the role or the molecule scenario.

The repo has no `molecule/default/molecule.yml` (no driver or platforms), so molecule can't run here. The new verify assertions have never executed.

- **New options:** `sshd_max_auth_tries` (default `4`) and `sshd_login_grace_time` (default `30`) are in `defaults/main.yml`. Each has its own `lineinfile` task in `tasks/main.yml`, written like the existing ones. They use the same `validate`, mode `0600` and `notify: Restart sshd`.
- **RedHat support:** `vars/Debian.yml` and `vars/RedHat.yml` set `sshd_package_name` and `sshd_service_name`. `ssh` is the service on Debian and `sshd` on RedHat. The package is `openssh-server` on both.
- **Task and handler changes:** the role loads the right file with `include_vars` on `os_family`. The install task and the restart handler now use those variables instead of hard-coded names.
- **Existing behaviour:** the Port, PermitRootLogin and PasswordAuthentication tasks are unchanged.
- **Metadata:** `meta/main.yml` now lists EL 8 and 9. I chose those versions myself, so change them if you target others.
- **Docs:** the README lists the two new variables, the supported platforms and the per-OS-family vars files.
- **Molecule verify:** `molecule/default/verify.yml` now also asserts that `MaxAuthTries 4` and `LoginGraceTime 30` are in the config. It also checks that `ssh.service` (Debian) or `sshd.service` (RedHat) exists.
