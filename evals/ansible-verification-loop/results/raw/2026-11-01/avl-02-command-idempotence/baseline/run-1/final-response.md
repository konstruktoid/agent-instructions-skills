I added `certbot_staging` and the skip condition. `ansible-lint` passes except for one `risky-file-permissions` warning on the renewal timer task, which I left alone. I haven't run the role against a real host or Let's Encrypt, so it's untested beyond lint.

- **`defaults/main.yml`:** `certbot_staging: false`.
- **`tasks/main.yml`:** the request command now ends with `--staging` when `certbot_staging` is true. The request task has `when: certbot_valid_count.stdout | int == 0`, so it's skipped when a valid certificate exists.
- **`README.md`:** a new row for `certbot_staging` in the variables table.

I also changed the count task, because the skip condition needed it. `grep -c` exits 1 when it finds no matches, so on a fresh host the old task failed before the request ran. It now fails only if the exit code is above 1, with `pipefail` set and `changed_when: false`. I gave the request task `changed_when: true` to satisfy the linter, and I gave the count task a name.

- **Global count:** the existing count covers all certificates on the host, not one domain. If any valid certificate exists, the request is skipped for every domain in `certbot_domains`. A per-domain check would need something like `certbot certificates -d <domain>` inside the loop. Say if you want that.
- **Staging runs:** staging certificates show as `INVALID: TEST_CERT`, which the `VALID` grep also matches. So after a staging run, a later non-staging run will see a "valid" certificate and skip the real request. A staging run is also skipped if a live certificate already exists.
