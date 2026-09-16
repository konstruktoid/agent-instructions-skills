No leftover test state (logs/caches went to `/home/user/.../home/tmp` and `/home/user/.../home/.cache`, both outside the working tree). Every changed/added file is one I intended to touch — nothing unrelated.

## Summary

**`MaxAuthTries` / `LoginGraceTime`** — added as `sshd_max_auth_tries` (default `4`) and `sshd_login_grace_time` (default `30`) in `defaults/main.yml`, applied via the same `lineinfile` + `sshd -T` validate pattern as the existing options in `tasks/main.yml`.

**RedHat support** — added `vars/Debian.yml` and `vars/RedHat.yml` holding `sshd_package_name`/`sshd_service_name` per OS family, loaded via `include_vars: "{{ ansible_facts['os_family'] }}.yml"`; `tasks/main.yml` and `handlers/main.yml` now use those vars instead of the hardcoded `openssh-server`/`ssh`. `meta/main.yml` gained an `EL` (versions `9`) platform entry alongside Debian.

**Fixes needed to make molecule verification actually pass** (none of these existed before — the repo had no `molecule.yml` at all, so this scenario had never been run):
- `molecule/default/molecule.yml` created, testing `debian-bookworm` and `rockylinux-9` via the `geerlingguy` systemd-capable images (plain `debian:bookworm`/`rockylinux:9` lack a running init, so the `service` module couldn't find `sshd` on Rocky and `/run/sshd` was never created on Debian).
- `molecule/default/converge.yml` fixed: `include_role: name: sshd_hardening` never matched the FQRN ansible-compat installs it as (`platform.sshd_hardening`, from `meta/main.yml`'s `author: platform`) — corrected to the FQRN.
- `tasks/main.yml` gained `update_cache: true` on the package install (fresh Debian containers have no apt cache), a `ssh-keygen -A` step (RockyLinux ships no host keys, so `sshd -T` validation failed), and a `/run/sshd` directory task (Debian's `sshd -T` needs it and nothing had created it yet).
- `molecule/default/verify.yml` extended to assert the new `MaxAuthTries`/`LoginGraceTime` values and that the correct service name is running per OS family.

**Verified**: `ansible-lint` clean (production profile, 0 findings) and full `molecule test` — converge, idempotence (0 changes on second run), verify, destroy — passes on both platforms.

**Docs**: README's variable table and supported-platforms line updated.

Files changed: `defaults/main.yml`, `handlers/main.yml`, `meta/main.yml`, `tasks/main.yml`, `README.md`, `molecule/default/converge.yml`, `molecule/default/verify.yml`, `molecule/default/molecule.yml` (new), `vars/Debian.yml` (new), `vars/RedHat.yml` (new).
