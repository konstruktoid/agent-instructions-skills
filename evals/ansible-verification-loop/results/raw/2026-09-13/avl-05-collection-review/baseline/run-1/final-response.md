`make test` passes: converge and idempotence both succeed, exit code 0. (The "missing" entries are unconfigured optional stages — `dependency`, `prepare`, `side_effect`, `verify`, `cleanup` — not failures; there's no `verify.yml`, so the scenario checks converge idempotence only.)

## Summary

`make test` (the README's documented entry point: `ansible-lint .` then `molecule test -s default`) **passes**, profile `production`. Files changed:

**Collection metadata**
- `galaxy.yml` — added required `tags`, `repository`; corrected description to match actual scope (Debian only)
- `meta/runtime.yml` — `requires_ansible` needed a patch-version qualifier (`>=2.15.0`)
- `changelogs/changelog.yaml` — added (ansible-lint's `galaxy[no-changelog]` requires one)
- `README.md` — corrected the "Debian and RedHat" claim; the role only ever targeted Debian

**Role (`roles/nftables_base`)**
- `defaults/main.yml`, `tasks/main.yml` — prefixed all role variables with `nftables_base_` (var-naming)
- `tasks/main.yml` — added `mode: "0644"` to the ruleset file, `changed_when` on command tasks, switched `nft list ruleset | wc -l` to a plain `nft list ruleset` command (dropped the risky shell pipe entirely)
- `tasks/main.yml` / `handlers/main.yml` — fixed a real bug: `ansible.builtin.package` failed against a Debian image with no apt cache (confirmed in a bare `debian:bookworm` container), so switched to `ansible.builtin.apt` with `update_cache: true`. Also found the ruleset-reload path was broken two ways at once: it force-applied `nft -f` unconditionally (non-idempotent) *and* separately notified a systemd service reload that can't work in an init-less container. Replaced both with one notify-driven handler that runs `nft -f` directly, plus `meta: flush_handlers` so the "check active ruleset" task still reflects the newly loaded rules.
- `molecule/default/molecule.yml` — added `NET_ADMIN`/`NET_RAW` capabilities; nftables needs them and the default Docker platform doesn't grant them

No linter configuration was weakened — `.ansible-lint`'s `profile: production` is unchanged, and every finding was fixed at the source.

/clear before starting anything unrelated — this task is done and the context is no longer needed.
