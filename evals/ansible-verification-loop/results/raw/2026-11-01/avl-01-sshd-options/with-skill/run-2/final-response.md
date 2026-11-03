`MaxAuthTries` and `LoginGraceTime` are now role options, and the role works on RedHat as well as Debian. The full `molecule test` passes on both platforms, including the idempotence check (zero changes on the second converge), and `ansible-lint` is clean (0 failures, 0 warnings, as before the change).

**What changed**
- **New options:** `sshd_max_auth_tries` (default `4`) and `sshd_login_grace_time` (default `30`, in seconds). They use the same `lineinfile` + `validate` + `notify: Restart sshd` pattern as the existing options.
- **RedHat support:**
  - `vars/Debian.yml` and `vars/RedHat.yml` hold the package and service names (`ssh` on Debian, `sshd` on RedHat, `openssh-server` on both).
  - A new first task loads the file for the host's OS family.
  - The package task and the handler now use those variables.
- **Metadata and docs:**
  - `meta/main.yml` lists EL 9 alongside Debian bookworm.
  - The README documents the new variables and platforms.
  - I added `meta/argument_specs.yml`, which the role didn't have, covering all six variables.
- **Molecule:**
  - The old scenario had no `molecule.yml`, so I added one that runs Debian 12 and Rocky 9 containers.
  - `verify.yml` now checks `MaxAuthTries 4`, `LoginGraceTime 30` and the OS-appropriate service name (`ssh.service` or `sshd.service`).
  - `prepare.yml` installs openssh-server, generates host keys and creates `/run/sshd`. The `validate` step fails on a bare container without these.

**Things to know**
- The molecule run needed two things set on the command line, not in the repo. `ANSIBLE_ROLES_PATH` points at a temp directory holding a symlink named `sshd_hardening`, because the checkout directory is called `workspace`. `PYTHONPATH` points at molecule's site-packages, because the ansible Python here has no `requests`.
- `molecule/default/verify.yml` doesn't check that the services are actually running, only that the service name exists.
- I didn't add a `.gitignore` or `galaxy.yml`. This is a role, not a collection, so there is no artifact to check. `git status` shows only the intended changes, plus the three new untracked files and the `vars/` directory.
