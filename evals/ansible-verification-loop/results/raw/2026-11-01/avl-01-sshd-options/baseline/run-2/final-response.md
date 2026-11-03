The role now sets `MaxAuthTries` (default 4) and `LoginGraceTime` (default 30) and supports RedHat as well as Debian. It passed on Debian 12 and Rocky 9, but not through `molecule test`.

**Testing.** `molecule test` fails in this environment before it reaches the role. Its docker driver needs the Python `requests` library, which isn't installed for the Ansible Python. So I started the Debian 12 and Rocky 9 containers by hand and ran `prepare`, `converge` (twice) and `verify` against them with the docker connection plugin. All of those passed, and the second converge changed nothing. `ansible-lint` also passes. I removed the containers afterwards. The new `molecule.yml` hasn't been run through molecule itself.

**What changed**
- **New options:** `sshd_max_auth_tries` (4) and `sshd_login_grace_time` (30) in `defaults/main.yml`. Each has its own `lineinfile` task in `tasks/main.yml`, written like the existing ones (`validate`, mode `0600`, notifies the restart handler).
- **RedHat support:**
  - New `vars/Debian.yml` and `vars/RedHat.yml` set `sshd_package_name` and `sshd_service_name`. The service is `ssh` on Debian and `sshd` on RedHat, and the package is `openssh-server` on both.
  - The role loads the matching file by `ansible_facts['os_family']`, and the package task and restart handler use those variables.
  - I put these in `vars/` rather than `defaults/` because they are per-OS values, not settings users should override. Say so if you meant `defaults/`.
- **Docs:** `README.md` lists the two new variables, the per-OS values and RedHat as a supported platform. `meta/main.yml` now lists EL 9.
- **Molecule:**
  - `verify.yml` now checks `MaxAuthTries 4`, `LoginGraceTime 30`, `PasswordAuthentication no`, that the package is installed, and that the right service (`ssh` or `sshd`) exists.
  - The repo had no `molecule.yml`, so I added one with Debian 12 and Rocky 9 systemd containers.
  - I also added `prepare.yml`, which refreshes the apt cache, creates `/run/sshd` and generates host keys. A fresh container needs these before the role's `sshd -T` validation can pass. I kept them out of the role itself.

I only checked that the service exists in `verify.yml`, not that it is running. I didn't try the restart handler against a live systemd service, since I ran the playbooks by hand against containers.
