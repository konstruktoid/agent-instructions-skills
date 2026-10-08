I added `certbot_staging` and the skip check. `ansible-lint` went from 6 violations to 1, and I haven't run the role itself.

**What changed**
- **`defaults/main.yml`:** `certbot_staging: false`.
- **`tasks/main.yml`:** the request task appends `--staging` when `certbot_staging` is true. It now loops over the per-domain results and skips a domain whose valid-certificate count is above 0.
- **`README.md`:** a `certbot_staging` row in the variables table, plus a sentence saying domains with a valid certificate are skipped.

**Where I departed from your request**
- **Per-domain count:** The existing check counted valid certificates across everything certbot knows about. Used as the skip condition, one valid certificate would have skipped every domain. I changed it to run `certbot certificates -d <domain>` once per domain, so the check is per domain.
- **`INVALID` matching:** The old `grep -c "VALID"` also matched `INVALID`, so I changed the pattern to `(VALID:`.
- **Zero matches:** `grep -c` exits 1 when it finds nothing, which would have failed the task. Exit codes 0 and 1 are now both accepted.
- **Lint fixes on touched tasks:** I fixed the lint findings on the two tasks I touched. The count task is named, uses `ansible.builtin.shell`, sets `pipefail` and has `changed_when: false`. The request task has `changed_when: true`.

**Verification**
- **Lint:** The one remaining violation is `risky-file-permissions` on the "Write the renewal timer" task. It was already failing before my change and I left it alone. I added no lint suppressions.
- **Tests:** The repo has no molecule, tox or CI setup, so no converge or idempotence run was possible. `certbot` also isn't available here, so nothing was exercised against Let's Encrypt.
- **Argument spec:** There is no `meta/argument_specs.yml` to update.

I left the repo uncommitted.
