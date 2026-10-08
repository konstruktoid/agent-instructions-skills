I added `MaxAuthTries`, `LoginGraceTime` and RedHat support, but the molecule scenario has not run. The repo has no `molecule/default/molecule.yml`, so `molecule list` exits with "glob failed". The only checks that ran were `ansible-lint`, which passed with 0 failures and 0 warnings both before and after, and `ansible-playbook --syntax-check` on `converge.yml` and `verify.yml`, which passed.

The role itself has never been converged. That means idempotence is unchecked, and the `RedHat` branch and the service-name assertion in `verify.yml` are untested. I did not invent a docker driver config and platform images, because that is a choice about your test infrastructure. Tell me which platforms you want and I'll add it.

**What changed**
- **New options:** `defaults/main.yml` has `sshd_max_auth_tries: 4` and `sshd_login_grace_time: 30`. Two new tasks in `tasks/main.yml` set them with the same `lineinfile` pattern as the existing options, including the `validate` check and the restart handler.
- **RedHat support:** the new `vars/Debian.yml` and `vars/RedHat.yml` set the package and service names. `tasks/main.yml` loads the file matching the `os_family` fact. The package is `openssh-server` on both families. The service is `ssh` on Debian and `sshd` on RedHat. The package task and the `Restart sshd` handler now read these variables.
- **Platforms and docs:** `meta/main.yml` now lists EL 9 alongside Debian bookworm, and the README documents the two variables and both platforms. I picked EL 9 as the RedHat version, so change it if you target something else.
- **Molecule verification:** `verify.yml` now asserts `MaxAuthTries 4` and `LoginGraceTime 30` in the config. It also asserts that the OS-family service name is present in the gathered service facts.

The role has no `meta/argument_specs.yml`, so there was nothing to update there. I didn't add one.

The syntax check needed a temporary role symlink in `/tmp/rp`. It sits outside the repo, and `git status` shows only the intended changes.
