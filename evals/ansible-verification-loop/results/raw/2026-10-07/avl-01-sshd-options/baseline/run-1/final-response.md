The role now sets `MaxAuthTries` and `LoginGraceTime`, and it works on RedHat as well as Debian. I ran the converge and verify playbooks against Debian 12 and Rocky Linux 9 containers, and both passed. `ansible-lint` also passes.

I could not run `molecule test` itself. Its docker driver fails here because its Python has no `requests` module. Instead I started the two containers with docker and ran `converge.yml`, `prepare.yml` and `verify.yml` against them with `ansible-playbook`. A second converge on both hosts reported no changes, so the role is still idempotent. I removed the containers afterwards.

**What changed**
- **New options:** `sshd_max_auth_tries` (default `4`) and `sshd_login_grace_time` (default `30`) are added in `defaults/main.yml`. Each has its own `lineinfile` task in `tasks/main.yml`, written the same way as the existing options (same `validate`, `mode` and `notify`).
- **RedHat support:** `tasks/main.yml` loads `vars/Debian.yml` or `vars/RedHat.yml` by `os_family`. These set `sshd_package_name` (`openssh-server` on both) and `sshd_service_name` (`ssh` on Debian, `sshd` on RedHat). The restart handler and the package task use those variables.
- **Docs and metadata:** the README now lists the new variables and both platforms, and `meta/main.yml` lists EL 9.
- **Verification:** `verify.yml` now checks that `MaxAuthTries 4` and `LoginGraceTime 30` each appear exactly once. It also checks that the right service name (`ssh` or `sshd`) exists for the OS family.

**Fix found by running it**
- On a fresh RedHat host, the `sshd -T` validation failed with "no hostkeys available". I added an `ssh-keygen -A` task that only creates missing keys, so it never reports a change.

**Molecule setup**
- The repo had no `molecule.yml`, so I added `molecule/default/molecule.yml` with `debian12` and `rockylinux9` platforms. I could not run it through molecule, so treat it as untested.
- I added `molecule/default/prepare.yml`. On Debian it refreshes the apt cache and creates `/run/sshd`, because the container never starts sshd and validation fails without that directory.
