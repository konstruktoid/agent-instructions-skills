`ansible-lint` now passes on the `production` profile with 0 failures and 0 warnings. Before my changes it reported 4 failures and no warnings. The role has no tests, `tox.ini` or molecule scenario, so lint was the only check I could run, and I did not render or apply the template.

**Lint fixes** (made by hand, not with `--fix`, so nothing else was reformatted):
- `tasks/main.yml`: the two task names now start with a capital letter (`name[casing]`).
- `tasks/main.yml`: `template` and `service` are now `ansible.builtin.template` and `ansible.builtin.service` (`fqcn[action-core]`).

**`ntp_client_min_sources`:**
- `defaults/main.yml`: added `ntp_client_min_sources: 2` with a comment, following the file's one-comment-per-variable layout.
- `templates/chrony.conf.j2`: added `minsources {{ ntp_client_min_sources }}` after `makestep`.
- `README.md`: added a row to the variables table that gives the default and says it is rendered as the `minsources` line.

The role has no `meta/argument_specs.yml`, so there was nothing to update there. I didn't create one.

I noticed one thing and left it alone because it's outside what you asked. The template task sets `group` from `ntp_client_conf_owner`, so the file's group always equals its owner. That may be intentional, but it could also be a missing `ntp_client_conf_group` variable.
