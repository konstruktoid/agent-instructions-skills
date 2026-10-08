The role now sets `MaxAuthTries` and `LoginGraceTime` and supports RedHat as well as Debian. I ran converge, a second converge, and verify on Debian 12 and Rocky 9 containers, and both were clean. The second converge changed nothing. `ansible-lint` also passes.

I ran those playbooks by hand against two Docker containers, not through `molecule test`. The molecule docker driver failed here because the controller's Python lacks `requests`. So `molecule/default/molecule.yml` is untested through molecule itself.

- **New options:** `sshd_max_auth_tries` (default `4`) and `sshd_login_grace_time` (default `30`) are applied with the same validated `lineinfile` pattern as the existing options. Both notify the restart handler.
- **RedHat support:** the package and service names now come from `vars/Debian.yml` and `vars/RedHat.yml`. They are `sshd_package_name` and `sshd_service_name`, set to `ssh` on Debian and `sshd` on RedHat. The tasks load the right file by OS family, and the handler uses the service variable. Both OS families use `openssh-server`, so the package name is the same on each.
- **Docs and metadata:** the README documents the two new variables and the supported platforms, and `meta/main.yml` lists EL 9.
- **Verification:** `verify.yml` now checks all five options in the config file. It also checks the effective `sshd -T` values, that the package is installed, and that the right service name (`ssh` or `sshd`) exists. I added `molecule.yml` with a Debian and a Rocky platform.
- **`prepare.yml` (new):** it refreshes the apt cache, generates host keys, and creates `/run/sshd`. Fresh containers need these before the role's `sshd -T` validation can pass.

I couldn't confirm that the `ssh` or `sshd` service restarts through the handler. The handler only runs on a config change, and it isn't covered by the repeat run. The verify step only checks that the service exists.
