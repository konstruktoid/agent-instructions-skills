I added `certbot_staging` (default `false`) and the skip condition. One caveat: the skip is global, not per domain, so it can skip domains that don't have a certificate yet. I haven't run the role itself, because the repo has no molecule scenario or tox config.

**What changed**
- **`defaults/main.yml`:** added `certbot_staging: false`.
- **`tasks/main.yml`:**
  - The certificate request appends ` --staging` when `certbot_staging` is true.
  - It runs only when `certbot_valid_count.stdout | int == 0`.
  - I added `changed_when: true` to the request, because lint requires it.
  - The count task was already there but didn't work: `grep -c` exits 1 when it finds zero matches, which would have failed the task on a fresh host. I gave it a name and the full `ansible.builtin.shell` name. I added `pipefail` and `changed_when: false`. I set `failed_when` to `rc > 1`, so zero valid certificates no longer fails it.
- **`README.md`:** added a row for `certbot_staging` that also notes the skip.
- **`meta/argument_specs.yml`:** the role doesn't have one, so I didn't add one.

**The caveat on the skip**
The existing count comes from `certbot certificates | grep -c VALID`, which counts valid certificates across all domains. If any domain already has a valid certificate, the request is skipped for every domain in `certbot_domains`, including new ones. Skipping per domain would need a per-domain check, for example `certbot certificates -d <domain>` inside the loop. I can make that change if you want it.

**Verification**
- `ansible-lint` went from 6 failures to 1. The remaining one is `risky-file-permissions` on the "Write the renewal timer" task, which was already failing and which I left alone because it's outside this request.
- Idempotence hasn't been tested.
- `git status` shows only the three intended files changed, with no leftover files.
