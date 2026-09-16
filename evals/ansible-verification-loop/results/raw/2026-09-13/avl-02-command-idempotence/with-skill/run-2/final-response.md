Only the three intended files changed, nothing untracked left behind, and no molecule/argument_specs files exist to update in this fixture.

**Changed files:**
- `defaults/main.yml` — added `certbot_staging: false`
- `tasks/main.yml` — per-domain valid-certificate check (`certbot certificates -d {{ item }}`) gates the `certonly` request via `when: item.stdout | int == 0`; `--staging` appended to the `certonly` command when `certbot_staging` is true. Also fixed FQCN, missing name, `risky-shell-pipe`, and `no-changed-when` findings on the two tasks this change touches.
- `README.md` — documented `certbot_staging`

**Verification:** `ansible-lint` findings dropped from 6 to 1 (the remaining `risky-file-permissions` on the unrelated "Write the renewal timer" task predates this change). Functional test with a stubbed `certbot` binary confirmed a domain with an existing valid cert is skipped, a domain without one is requested, and `--staging` is appended only when `certbot_staging: true` (verified both branches, including no trailing artifact in the command when false).

I dropped the skill's argument-spec check because no `meta/argument_specs.yml` exists in this role, and skipped molecule/test-fixture updates because no test harness is present in this fixture.

Recommend `/clear` before starting unrelated work.
