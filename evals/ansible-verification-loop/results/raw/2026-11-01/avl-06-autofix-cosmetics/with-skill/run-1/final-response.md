The role now lints clean, and `ntp_client_min_sources` is in place.

`ansible-lint` on the `production` profile went from 4 failures to 0 failures and 0 warnings. The role has no `meta/argument_specs.yml`, so there was no spec to update.

**Lint fixes** (`tasks/main.yml`):
- Both task names now start with a capital letter ("Render…", "Manage…").
- `template` and `service` are now `ansible.builtin.template` and `ansible.builtin.service`.

**New variable:**
- `defaults/main.yml`: `ntp_client_min_sources: 2`, with a comment above it.
- `templates/chrony.conf.j2`: ends with `minsources {{ ntp_client_min_sources }}`.
- `README.md`: a new row in the variables table.

I made the edits by hand rather than with `--fix`, so nothing else was reformatted. The mixed quoting in `defaults/main.yml` is untouched.

**Not run:**
- The role has no molecule or tox tests, so lint was the only check.
- I didn't render the template, so `minsources` is untested against a real chrony.
