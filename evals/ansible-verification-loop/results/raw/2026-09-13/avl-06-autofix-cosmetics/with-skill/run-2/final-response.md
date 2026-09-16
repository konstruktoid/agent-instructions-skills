Diff is minimal and every hunk is explained — no unrelated formatting changes. No molecule/tox setup exists in this role (single-role checkout, no `roles/`, no `molecule/`, no `tox.ini`), so ansible-lint is the only verification gate available; it now passes cleanly on the `production` profile.

Files changed: `tasks/main.yml`, `defaults/main.yml`, `templates/chrony.conf.j2`, `README.md`.

- Fixed all 4 lint findings (2× `name[casing]`, 2× `fqcn[action-core]`) in `tasks/main.yml`.
- Added `ntp_client_min_sources` (default `2`) to `defaults/main.yml`, rendered as `minsources` in `chrony.conf.j2`, documented in `README.md`.
- No `meta/argument_specs.yml` exists in this role, so nothing to sync there.

/clear before starting anything unrelated.
