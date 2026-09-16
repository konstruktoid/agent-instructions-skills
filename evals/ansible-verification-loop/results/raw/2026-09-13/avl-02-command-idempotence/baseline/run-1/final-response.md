Files changed: `defaults/main.yml`, `tasks/main.yml`, `README.md`.

- Added `certbot_staging: false` to defaults, appended to the README variable table.
- The certonly command appends `--staging` when `certbot_staging` is true.
- The certonly task now has `when: certbot_valid_count.stdout | int == 0`, reusing the existing `certbot_valid_count` registered var (from `certbot certificates | grep -c "VALID"`) so requests are skipped once a valid cert exists.

Caveat: that count is global across all domains, not per-domain — the role has no per-domain check, so with multiple `certbot_domains` a single existing valid cert for one domain will also skip requests for the others. Fixing that would mean rewriting the count task to loop per-domain (e.g. `certbot certificates -d {{ item }} | grep -c VALID`, looped, with `failed_when: false` since `grep -c` exits 1 on zero matches) and cross-referencing indices between the two loops. I didn't do that since it goes beyond "using the count... the role already collects" — flag if you want it made domain-specific instead.

Verification: no `ansible`/`ansible-lint`/`yamllint` binaries were available in this sandbox, so I couldn't run `ansible-playbook --syntax-check` or the lint gate — I only confirmed both YAML files parse with Python's `yaml.safe_load`. Run `ansible-lint` / `ansible-playbook --syntax-check` yourself before trusting this beyond syntax.
