`ansible-lint` now passes cleanly on the `production` profile, down from 4 violations. I didn't render the template or run the role, so the `minsources` line is untested beyond the lint pass.

**Lint fixes** (all in `tasks/main.yml`; I edited by hand and didn't use `--fix`):
- Both task names now start with a capital letter ("Render…" and "Manage…").
- `template` and `service` now use their full module names, `ansible.builtin.template` and `ansible.builtin.service`.

**New `ntp_client_min_sources` variable:**
- `defaults/main.yml` sets it to `2`, with a comment like the other defaults.
- `templates/chrony.conf.j2` renders it as `minsources {{ ntp_client_min_sources }}`.
- `README.md` documents it in the variables table.

Nothing else in the touched files was reformatted.
