No molecule/tox/test setup exists in this role — nothing to update there. Lint is the only verification gate present, and it's clean on the `production` profile (was 4 failures, now 0).

**Files changed:** `tasks/main.yml`, `defaults/main.yml`, `templates/chrony.conf.j2`, `README.md`

- `tasks/main.yml`: capitalized the two task names and switched `template`/`service` to FQCN — the 4 lint findings.
- `defaults/main.yml`: added `ntp_client_min_sources: 2`.
- `templates/chrony.conf.j2`: renders it as `minsources {{ ntp_client_min_sources }}`.
- `README.md`: documented the new variable.

No `meta/argument_specs.yml` exists in this role, so there's nothing to sync there. No molecule/tox test harness exists either — lint was the only available gate.
