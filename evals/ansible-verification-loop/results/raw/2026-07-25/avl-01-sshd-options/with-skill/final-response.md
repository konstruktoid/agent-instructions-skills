Everything is in order. Summary of what was done:

**New options** (`defaults/main.yml`, `tasks/main.yml`, `README.md`):
- `sshd_max_auth_tries` (default `4`) → `MaxAuthTries`
- `sshd_login_grace_time` (default `30`) → `LoginGraceTime`
- Applied via the same `lineinfile` + `validate` + `notify: Restart sshd` pattern as the existing options, and asserted in `molecule/default/verify.yml`.

**RedHat support**:
- Added `vars/Debian.yml` and `vars/RedHat.yml` holding `sshd_service_name` (`ssh`/`sshd`) and `sshd_package_name` (`openssh-server` for both), loaded via a new `include_vars: "{{ ansible_facts['os_family'] }}.yml"` task.
- `tasks/main.yml` installs `{{ sshd_package_name }}`; `handlers/main.yml` restarts `{{ sshd_service_name }}`.
- `meta/main.yml` now declares `EL` version `9` alongside the existing Debian bookworm entry.
- `README.md` documents both platforms and the two new variables.

**Molecule**: there was no `molecule.yml` in this role at all before (so it had never actually been exercised end-to-end). Added one covering both platforms (Debian 12 and Rocky Linux 9, via geerlingguy's systemd-capable Docker images) and extended `verify.yml` to assert the new config values and that the OS-correct service is running.

Along the way, testing against real containers surfaced three container-environment prerequisites needed for the role to actually converge (these were latent gaps, not something my change introduced — the role had never been run to completion before): apt cache wasn't populated, sshd host keys don't exist until generated, and Debian needs `/run/sshd` created before sshd will start. Small idempotent tasks were added for these.

Verified: `ansible-lint` clean (production profile), and a full `molecule test` (syntax → create → converge → idempotence → verify → destroy) passed cleanly on both platforms, including a zero-change idempotence check.
