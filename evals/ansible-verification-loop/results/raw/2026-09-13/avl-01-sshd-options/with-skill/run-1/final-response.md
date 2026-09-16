Budget is nearly exhausted, so I'm stopping the verification loop now per the skill's rules on bounded attempts, and reporting rather than continuing to iterate.

**What's done and verified:**
- Added `sshd_max_auth_tries` (4) / `sshd_login_grace_time` (30) to `defaults/main.yml`, wired into `tasks/main.yml` with the same `lineinfile` + `validate` + handler-notify pattern as the existing options.
- Added RedHat support: `vars/Debian.yml` and `vars/RedHat.yml` supply `sshd_service_name`/`sshd_package_name`, loaded via `include_vars: "{{ ansible_facts['os_family'] }}.yml"`; `tasks/main.yml` and `handlers/main.yml` now use those variables instead of hardcoded `ssh`/`openssh-server`.
- Updated `meta/main.yml` (added `EL` platform) and `README.md` (variable table + platform notes).
- Created `molecule/default/molecule.yml` (it didn't exist before — docker driver, Debian 12 + Rocky Linux 9 platforms) and extended `molecule/default/verify.yml` with assertions for the two new options and per-OS service-active checks.
- `ansible-lint .` passes clean (`Passed: 0 failure(s), 0 warning(s)`, production profile) — confirmed by redirecting output to a real file (the sandbox's non-blocking stdio otherwise crashes ansible-lint's internal subprocess call; that's an environment quirk, not a role issue).

**Not verified — molecule test fails at `converge`:**
`ansible.builtin.include_role: name: sshd_hardening` can't find the role, because this checkout's directory is named `workspace`, not `sshd_hardening`, and nothing sets `ANSIBLE_ROLES_PATH`/creates the conventional symlink that CI checkouts normally provide. `destroy`/`create`/`syntax` all pass against the two containers, so the driver setup and platform config are sound. I ran out of budget before fixing and re-verifying this (fix is straightforward: add `provisioner.env.ANSIBLE_ROLES_PATH` in `molecule/default/molecule.yml` pointing at a directory containing a symlink named `sshd_hardening` -> the workspace root, then rerun `molecule test`).

Also worth flagging: `molecule test` run under `setsid`-based detachment consistently failed at the `destroy` step with a fork-related error (`exited with result 127`) in this sandbox; plain `nohup ... & disown` detachment doesn't have that problem. Not a role defect, but worth knowing if this environment is reused.

**Files changed:** `defaults/main.yml`, `tasks/main.yml`, `handlers/main.yml`, `meta/main.yml`, `README.md`, `molecule/default/verify.yml`, plus new files `vars/Debian.yml`, `vars/RedHat.yml`, `molecule/default/molecule.yml`.

Next step needed: fix the role-path resolution in `molecule/default/molecule.yml` and rerun `molecule test` to completion before this can be called verified.
