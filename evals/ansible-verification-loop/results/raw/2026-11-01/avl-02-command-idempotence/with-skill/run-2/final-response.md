I've added the variable and the skip condition, and lint is down to one pre-existing finding. I'm about to write up the result. This role has no molecule scenario, `tox.ini` or `argument_specs.yml`, so lint is the only check I could run.

**Changes**
- `defaults/main.yml`: added `certbot_staging: false`.
- `tasks/main.yml`:
  - The request command appends ` --staging` when `certbot_staging` is true.
  - The request task now has `when: certbot_valid_count.stdout | int == 0`.
- `README.md`: added a `certbot_staging` row to the variables table.

**Fixes in the tasks I touched**
- The count task needed `pipefail` and a name, and `grep -c` exits 1 when it finds no certificates. I gave it `failed_when: rc > 1` and `changed_when: false`, so a fresh host no longer fails there.
- The request task gets `changed_when: true`, because lint required one.

**Lint**: before the change `ansible-lint` reported 6 failures. Now it reports 1: `risky-file-permissions` on the "Write the renewal timer" task, which was already there. I left it alone because it's unrelated to this change.

**Not verified**
- Nothing was run against certbot or a container, so the idempotence check was not done.
- `--staging` has not been exercised against Let's Encrypt.

**Skip is not per domain**: `certbot_valid_count` counts valid certificates across the whole host, not for each domain. If any valid certificate exists, requests for every domain are skipped, including a newly added one. Checking each domain separately would need a per-domain `certbot certificates -d <domain>` check. I haven't built that, so say if you want it.
