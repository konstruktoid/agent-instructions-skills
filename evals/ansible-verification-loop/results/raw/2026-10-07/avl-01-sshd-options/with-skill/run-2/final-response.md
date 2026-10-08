The role now supports `MaxAuthTries` (default 4) and `LoginGraceTime` (default 30) on both Debian and RedHat. `ansible-lint` passes with 0 failures and 0 warnings, the same as before my changes. A full `molecule test` passes on Debian 12 and Rocky 9, including the idempotence check and the verify step.

**Role changes**
- **New options:** `sshd_max_auth_tries` and `sshd_login_grace_time` are in `defaults/main.yml`. Each has a `lineinfile` task written like the existing ones, with the same `validate` and `notify`.
- **RedHat support:** `tasks/main.yml` loads `vars/Debian.yml` or `vars/RedHat.yml` by OS family. These set `sshd_package_name` and `sshd_service_name` (`ssh` on Debian, `sshd` on RedHat). The package task and the restart handler now use them. Both families use `openssh-server`.
- **Host keys on RedHat:** I added an `ssh-keygen -A` task for RedHat that skips if the keys already exist. A freshly installed RedHat package has no host keys until sshd first starts. Without them the existing `sshd -T` validation fails, and that failure showed up in the first Rocky run.
- **Metadata and docs:** `meta/main.yml` now lists EL 9, and the README covers the new variables, the per-family variables and the supported platforms.

**Molecule changes**
- The repo had no `molecule.yml`, so I added one for the docker driver with Debian 12 and Rocky 9 containers.
- I added `prepare.yml`, which refreshes the apt cache and creates `/run/sshd` on Debian. The containers need both, because sshd never starts in them. Real Debian hosts don't need this.
- `verify.yml` now checks `MaxAuthTries 4` and `LoginGraceTime 30` in the config. It also checks that the OS-appropriate service (`ssh` or `sshd`) exists.

**Things to know**
- There is no `meta/argument_specs.yml` in this role, so I didn't create one. Say if you want it added.
- On this machine molecule only ran with its own tool environment first on `PATH`. Otherwise the docker driver's playbook failed with a missing `requests` library. That's a local setup issue, not a role issue.
- `git status` shows only my intended changes: six modified files, plus the new `molecule.yml`, `prepare.yml` and `vars/`. Nothing from the test run was left behind in the repo.

I didn't commit anything.
