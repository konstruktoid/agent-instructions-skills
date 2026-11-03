The role changes are written and `ansible-lint` is clean, but I couldn't run the molecule test, so the converge, idempotence and verify steps haven't been checked.

**Molecule failure.** `molecule test` fails at the first `destroy` step, before any converge. The error is `Failed to import the required Python library (requests)` on `/tmp/eval-tools/ansible-core/bin/python`. That's the Python ansible-core uses for the localhost docker tasks in this sandbox. The molecule tool's own Python has `requests` and `docker`. I made two attempts. The second pointed `ANSIBLE_PYTHON_INTERPRETER` at the molecule Python, which had no effect. I stopped there, since the same error came back. No containers were left behind. To get a real run, install `requests` and `docker` into the ansible-core Python, or set `ansible_python_interpreter` for localhost in `molecule.yml`, then run `molecule test`.

**What changed**
- **New options:** `sshd_max_auth_tries` (default 4) and `sshd_login_grace_time` (default 30). Each has its own `lineinfile` task written like the existing ones, with the same validate, mode and notify.
- **RedHat support:** `vars/Debian.yml` and `vars/RedHat.yml` set `sshd_package` and `sshd_service` (`ssh` on Debian, `sshd` on RedHat). `tasks/main.yml` loads them with `include_vars` by `os_family`. The install task and the restart handler now use those variables.
- **Metadata and docs:** `meta/main.yml` now lists EL 9. The README documents the new variables and the platforms. I also added `meta/argument_specs.yml` covering every variable, because the role had none.
- **Molecule:** `verify.yml` now checks `MaxAuthTries 4`, `LoginGraceTime 30` and that the OS-appropriate service exists. The scenario had no `molecule.yml`, so I added one with a `debian12` and a `rocky9` platform, using the geerlingguy systemd images already on this machine.

**Lint:** `ansible-lint` gives 0 failures and 0 warnings both before and after the change, with no suppressions added.

**Repo state:** no test leftovers are untracked, and there is no `galaxy.yml` because this is a role, not a collection. Nothing is committed.
