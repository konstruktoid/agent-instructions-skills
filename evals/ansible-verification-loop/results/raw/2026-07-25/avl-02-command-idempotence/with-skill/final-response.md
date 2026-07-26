Done. Summary of changes in `certbot_renewal`:

- **`defaults/main.yml`**: added `certbot_staging: false`.
- **`tasks/main.yml`**:
  - Renamed/fixed the pre-existing valid-cert-count task (`ansible.builtin.shell` FQCN, `set -o pipefail`, `changed_when: false`) since it's read-only.
  - Certificate request now appends `--staging` when `certbot_staging` is true, and is skipped entirely via `when: certbot_valid_count.stdout | int == 0` — reusing the count the role already collects rather than adding a new lookup.
  - Added `mode: "0644"` to the timer file write (pre-existing lint finding, fixed while touching the file).
- **`README.md`**: documented `certbot_staging` in the variable table.

`ansible-lint` (production profile) and an `ansible-playbook --syntax-check` both pass clean; no molecule/tox setup exists in this fixture to run further. No unrelated files were touched.
