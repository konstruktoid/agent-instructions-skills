I added `MaxAuthTries` and `LoginGraceTime` and RedHat support, but the molecule scenario has not been run. `ansible-lint` passes and a syntax check of the role is clean.

**Why molecule did not run:** the repo has no `molecule/default/molecule.yml`, so there is no driver or platform definition to converge against. Docker is available here, but I didn't invent a platform config. I also didn't check idempotence or the RedHat path on a real host. The updated `verify.yml` has never executed. I'd add a `molecule.yml` with a Debian and a RedHat systemd container, then run `molecule test` to confirm.

**Options**
- `sshd_max_auth_tries` defaults to 4 and `sshd_login_grace_time` defaults to 30. Both are applied with `lineinfile`, `validate` and `notify: Restart sshd`, the same way as the existing options.

**RedHat support**
- `tasks/main.yml` loads `vars/<os_family>.yml` first. `vars/Debian.yml` and `vars/RedHat.yml` each set `sshd_package_name` and `sshd_service_name` (`openssh-server` for both; `ssh` on Debian, `sshd` on RedHat).
- The install task and the restart handler now use those variables.
- `meta/main.yml` lists EL 9 as a platform. I picked EL 9 myself, so change it if you target other versions.

**Docs and tests**
- The README lists the two new variables and the per-OS package and service names.
- I added `meta/argument_specs.yml`, which the role didn't have before, covering all variables.
- `verify.yml` now also asserts `MaxAuthTries 4` and `LoginGraceTime 30`. It checks that the service for the host's OS family is running (`sshd.service` on RedHat, `ssh.service` on Debian).

Lint output is unchanged apart from the new files, with no suppressions added. The only untracked files are the new `meta/argument_specs.yml` and `vars/`, and nothing was committed.
