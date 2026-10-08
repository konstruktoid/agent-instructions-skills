`certbot_staging` (default `false`) now adds `--staging` to the certificate request. The request is also skipped when a valid certificate already exists. Lint went from 6 findings to 1, but I couldn't run the role, so the new behaviour is untested.

**Changes**
- **`defaults/main.yml`:** added `certbot_staging: false`.
- **`tasks/main.yml`:** the request appends `--staging` when the variable is true. It only runs when `certbot_valid_count.stdout | int == 0`.
- **`README.md`:** added a row for `certbot_staging` and a note about the skip condition.

**Fixes to the count task**
- The old `grep -c` exits 1 when it counts zero, which would have failed the task on a fresh host. The new `failed_when` only treats an exit code above 1 as a failure.
- `grep "VALID"` also matches `INVALID`, so expired and staging certificates were being counted as live. The pattern is now `(VALID:`.
- I also gave the task a name, switched it to `ansible.builtin.shell`, added `pipefail` and `changed_when: false`.
- The request task now has `changed_when: true`, which clears the other `no-changed-when` finding.

**Verification**
- `ansible-lint` (production profile) had 6 findings before and has 1 now. The remaining one is `risky-file-permissions` on the renewal timer `copy`, which was there before and which I left alone. No suppressions were added.
- The repo has no molecule scenarios, tox config or `meta/argument_specs.yml`, so there was nothing else to run or update. I did not run the role against a real host or the staging endpoint.
- `git status` shows only the three files above.

**Skip condition is host-wide**
The count covers every certificate on the host, not just the one for each domain. If any valid certificate exists, requests for all domains are skipped, including a newly added one. Checking each domain properly would mean looking at `certbot certificates -d <domain>` inside the loop. I stuck to the count the role already collects, as you asked, and noted the limit in the README. Say if you want the per-domain check.
