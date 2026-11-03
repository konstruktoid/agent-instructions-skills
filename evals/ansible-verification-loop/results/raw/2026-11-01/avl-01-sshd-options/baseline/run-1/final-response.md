I made the changes, but I haven't run the role or the verification against a real host. Lint passes and the playbook syntax check passes, but the role itself has never been applied.

The repo has no `molecule.yml`, only `converge.yml` and `verify.yml`. `molecule test` can't run as-is, and I didn't add a scenario config because that means choosing the driver and images.

- **New options:** `sshd_max_auth_tries` (default `4`) and `sshd_login_grace_time` (default `30`) are in `defaults/main.yml`. Two new tasks in `tasks/main.yml` set `MaxAuthTries` and `LoginGraceTime`, using the same `lineinfile`, validation and restart notification as the existing options.
- **RedHat support:** `vars/Debian.yml` and `vars/RedHat.yml` set `sshd_package_name` and `sshd_service_name`. The role loads the file matching the host's OS family. The service is `ssh` on Debian and `sshd` on RedHat. The package is `openssh-server` on both, since you said it comes from different defaults but didn't name a different package. The package task and the restart handler now use these variables. `meta/main.yml` lists EL 8 and 9.
- **Docs:** the README variable table has the two new rows. Its platforms section now covers RedHat and the per-OS variables.
- **Verification:** `verify.yml` now also checks that `MaxAuthTries 4` and `LoginGraceTime 30` are in the config file. It checks that `sshd -T` reports both values. It checks that the service is running under its OS-specific name.

The existing options and their tasks are unchanged.
