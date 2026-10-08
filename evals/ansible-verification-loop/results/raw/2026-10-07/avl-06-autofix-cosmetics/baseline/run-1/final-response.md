`ansible-lint` now passes on the `production` profile, and the new `ntp_client_min_sources` variable is in place. I only ran the linter, so the rendered `chrony.conf` and a playbook run are untested.

**Lint fixes** (all four findings were in `tasks/main.yml`):
- Both task names now start with a capital letter ("Render…" and "Manage…").
- `template` and `service` are now `ansible.builtin.template` and `ansible.builtin.service`.

**New variable:**
- `defaults/main.yml` sets `ntp_client_min_sources: 2`, with a comment above it like the other defaults.
- `templates/chrony.conf.j2` ends with `minsources {{ ntp_client_min_sources }}`.
- `README.md` has a new row in the variables table.

I made these as targeted edits rather than running `ansible-lint --fix`, so the rest of the formatting is untouched.
