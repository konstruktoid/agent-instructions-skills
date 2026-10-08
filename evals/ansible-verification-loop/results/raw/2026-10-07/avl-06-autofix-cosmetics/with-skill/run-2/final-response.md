`ansible-lint` now passes on the production profile with 0 failures and 0 warnings. The role has no molecule, tox, or other test setup, and I didn't run any tests. Lint is the only check I ran.

**Lint findings cleared (4):**
- Both task names in `tasks/main.yml` now start with a capital letter (`name[casing]`).
- `template` and `service` in `tasks/main.yml` are now `ansible.builtin.template` and `ansible.builtin.service` (`fqcn[action-core]`).

I made these edits by hand rather than with `--fix`, so the diff touches only the changed lines and leaves the other formatting alone.

**`ntp_client_min_sources`:**
- `defaults/main.yml` sets it to `2`, with a comment in the same style as the other variables.
- `templates/chrony.conf.j2` renders it as `minsources {{ ntp_client_min_sources }}`, added after `makestep`.
- `README.md` has a new row in the variables table.

The role has no `meta/argument_specs.yml`, so there was nothing to update there, and I didn't create one.
