The role changes are written and `ansible-lint` passes, but `molecule test` never ran against the containers, so none of it has been tested.

**What I changed**
- **New options:** `sshd_max_auth_tries` (default `4`) and `sshd_login_grace_time` (default `30`) are in `defaults/main.yml`. Two new `lineinfile` tasks in `tasks/main.yml` apply them, written the same way as the existing options: regexp, `sshd -T` validate, mode `0600`, and notify the restart handler.
- **RedHat support:**
  - New `vars/Debian.yml` and `vars/RedHat.yml` define `sshd_package_name` and `sshd_service_name`. The service is `ssh` on Debian and `sshd` on RedHat, and the package is `openssh-server` on both.
  - The role loads the right file with `include_vars` on the `os_family` fact. The install task and the handler now use those variables.
  - `meta/main.yml` lists EL 9 as a platform.
- **Docs:** the README covers the new variables and both platforms. I added `meta/argument_specs.yml`, which didn't exist, covering all six variables.
- **Molecule:** `verify.yml` now asserts `MaxAuthTries 4` and `LoginGraceTime 30` in the file. It also checks `maxauthtries 4` and `logingracetime 30` in the output of `sshd -T`. The default scenario had no `molecule.yml`, so I added one with the Docker driver and two platforms, Debian 12 and Rocky 9.

**Verification**
- `ansible-lint` gives 0 failures and 0 warnings, the same as before my change.
- Three attempts at the molecule run all failed in the Docker driver's create and destroy steps. The ansible-core environment (`/tmp/eval-tools/ansible-core`) has no `requests` library, so the Docker modules fail with "Failed to import the required Python library (requests)".
- I tried an `ANSIBLE_PYTHON_INTERPRETER` override, then `-e ansible_python_interpreter=` pointing at the molecule venv, which does have `requests`. Neither took effect, so I stopped rather than keep guessing. The converge, idempotence and verify steps were never reached against the new containers.
- Next step: install `requests` and `docker` into the ansible-core environment, or run molecule from an environment that has them, then run `molecule test`.
- The `/tmp/ansible-verify-*` logs I first looked at were older runs from other sessions, so I ignored them.
- The working tree has only the intended changes. I didn't touch the existing Docker containers `sshd-debian`, `sshd-rockylinux`, `avl-debian` and `avl-rocky`, since they aren't mine.
