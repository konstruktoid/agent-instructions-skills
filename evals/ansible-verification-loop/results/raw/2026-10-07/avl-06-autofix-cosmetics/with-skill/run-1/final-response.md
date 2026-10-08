`ansible-lint` now passes on the `production` profile with 0 failures and 0 warnings. It was failing with 4 findings.

**Lint fixes** (`tasks/main.yml`):
- The two task names now start with an uppercase letter.
- `template` is now `ansible.builtin.template`, and `service` is now `ansible.builtin.service`.

I made these as hand edits rather than with `--fix`, so the rest of the file's formatting is unchanged. The diff is 9 insertions and 4 deletions across 4 files.

**New variable:**
- **Default:** `defaults/main.yml` sets `ntp_client_min_sources: 2`, with a comment in the same style as the other variables.
- **Template:** `templates/chrony.conf.j2` renders `minsources {{ ntp_client_min_sources }}` after the `makestep` line.
- **README:** The variables table has a new row for it.

**Not run:** The role has no molecule scenarios, tox config or `meta/argument_specs.yml`, so there was no test suite to run and no argument spec to update. I did not render the template or converge the role, so the `minsources` line is untested beyond lint.
