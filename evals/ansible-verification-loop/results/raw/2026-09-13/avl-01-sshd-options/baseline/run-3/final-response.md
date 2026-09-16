Done. `molecule test` (converge, idempotence, verify) passed cleanly on both a Debian and a RedHat-family instance; `ansible-lint` passes at the `production` profile.

**Changes:**
- `defaults/main.yml` — added `sshd_max_auth_tries: 4`, `sshd_login_grace_time: 30`
- `tasks/main.yml` — includes OS-family vars, uses `sshd_package_name`, installs with `update_cache: true`, generates SSH host keys and the `/run/sshd` privsep directory (both were missing on the minimal RedHat image and blocked the `sshd -T` validate step), and adds `MaxAuthTries`/`LoginGraceTime` lineinfile tasks
- `handlers/main.yml` — service name now `{{ sshd_service_name }}`
- `vars/Debian.yml`, `vars/RedHat.yml` (new) — `sshd_service_name`/`sshd_package_name` per OS family (`ssh`/`sshd`, both from `openssh-server`)
- `meta/main.yml` — added EL 9 platform
- `README.md` — documented new variables and RedHat support
- `molecule/default/verify.yml` — asserts on `MaxAuthTries`, `LoginGraceTime`, and that the OS-correct service is running
- `molecule/default/molecule.yml` (new, none existed before) — docker driver with a Debian 12 and a Rocky Linux 9 instance (systemd-in-docker via `geerlingguy/docker-*-ansible` images)
- `molecule/default/roles/sshd_hardening` — symlink to the repo root, needed because the checkout directory is named `workspace` rather than `sshd_hardening`, so `include_role: name: sshd_hardening` in `converge.yml` can resolve it

Per your CLAUDE.md, I haven't staged or committed anything — let me know if you want that done. This session ran a full molecule test cycle (creates/destroys docker containers); nothing outside the working tree was left behind. Worth a `/clear` before starting unrelated work.
