I added `certbot_staging`, but I only ran `ansible-lint`. I haven't run the role against a host or against Let's Encrypt staging.

- **Variable:** `certbot_staging` defaults to `false` in `defaults/main.yml`. When it's true, the request task appends `--staging` to the certbot command.
- **Skip condition:** the request task now has `when: certbot_valid_count.stdout | int == 0`, so it's skipped when the role's valid-certificate count is above zero.
- **Count task fix:** I also fixed the existing count task. `grep -c` exits with code 1 when it finds zero matches, which would have failed the play on a fresh host before any request ran. The task now only fails on an rc above 1 and no longer reports `changed`. I also gave it a name.
- **README:** I added a row for `certbot_staging` to the variables table.

- **Limitation:** the count is across all certificates on the host, not per domain. If any valid certificate exists, every domain in `certbot_domains` is skipped, including a newly added one. A per-domain check, such as running `certbot certificates -d <domain>` inside the loop, would fix that. I held back because you asked to use the existing count.
- **Staging certs count as valid:** certbot lists staging certificates as `INVALID: TEST_CERT`, and the `VALID` match also hits that string. A staging dry run therefore counts as a live certificate, and a later real run would be skipped.
- **Remaining `ansible-lint` findings:** the count task's pipe has no `pipefail`, the request task has no `changed_when`, and the timer `copy` has no `mode`. All three were there before my change, and I left them alone.
