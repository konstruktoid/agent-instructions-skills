YAML is valid; `ansible`/`ansible-lint` aren't installed in this environment, so I couldn't run `--syntax-check` or lint — only manual review.

Changed files:
- `defaults/main.yml` — added `certbot_staging: false`
- `tasks/main.yml` — cert request now skips via `when: certbot_valid_count.stdout | int == 0` (reusing the existing `certbot_valid_count` registered var) and appends `--staging` when `certbot_staging` is true
- `README.md` — documented `certbot_staging`

One caveat worth flagging: `certbot_valid_count` is a single global count across all certs (`certbot certificates | grep -c VALID`), not per-domain. So with multiple `certbot_domains`, one valid cert anywhere skips the entire loop, not just the domain that already has one. That's a limitation of reusing the existing collected count as instructed rather than adding per-domain detection — say if you want it scoped per-domain instead.
