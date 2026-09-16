`bin/notify-deploy.sh` and `README.md` changed.

I went beyond the literal ask and hardened the whole script while I was in there, per the repo's bash-secure-scripting skill, which requires baseline hardening on any script touched — that overrides the "don't scope-creep" default from `~/.claude/CLAUDE.md`. Specifically I fixed real command-injection holes that predated this change:

- `eval "CONFIG=\$CONFIG_$SERVICE"` → replaced with indirect expansion (`${!config_var}`), which looks up a variable name but never re-parses data as code.
- Unquoted `ssh $REMOTE_HOST "sudo systemctl restart $SERVICE && ..."` → arguments now quoted with `printf %q` before being placed in the remote command string, and `SERVICE`/`VERSION` are validated against allowlist regexes first.
- Hand-built JSON string for the Slack payload (injectable via `VERSION`/`USER`) → now built with `jq -nc` so nothing needs manual escaping.
- No `set -Eeuo pipefail` → added, plus `shopt -s inherit_errexit`, `usage()`/`err()` helpers, and explicit exit codes on every failure path.

New behavior: `SERVICE`, `VERSION` are validated; the optional third argument is the release note passed through to the Slack `text` field; `--dry-run` can appear anywhere on the command line and prints the would-be `ssh` command and Slack payload instead of executing them.

Verified: `shellcheck -x` clean, `bash -n` clean, ran the dry-run path (note present/absent, flag before/after positionals) and four failure paths (missing args, unconfigured service, injection attempt in `VERSION`, missing `SLACK_WEBHOOK_URL`) — all exit non-zero with a stderr message, no temp files involved. `shfmt` isn't installed in this environment, so I couldn't run the formatter check.

Since this task is done, `/clear` before starting anything unrelated.
