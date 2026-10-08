I couldn't make this change. There's no container entrypoint script in this repo, and this session has no tools to edit files or run commands.

**What's there:**
- `Dockerfile` has no `ENTRYPOINT`. It just runs `CMD ["python", "-m", "app"]`.
- `scripts/backup.sh` is the only shell script, and it's a nightly backup job, not an entrypoint.

So this would mean creating a new script, not adding to an existing one. Before I write it, I need to know how the app should receive the config:
1. As a flag: `python -m app --config PATH`?
2. As an environment variable, e.g. `APP_CONFIG=PATH`?
3. Or is there an entrypoint somewhere else (another repo, a base image) that you meant?

Here's a draft that assumes option 1. I haven't run it or checked it with `shellcheck` or `bash -n`:

```bash
#!/usr/bin/env bash
#
# Container entrypoint: accepts an optional --config PATH, then execs the app
# with every remaining argument passed through unchanged.

set -Eeuo pipefail
shopt -s inherit_errexit

readonly PROGNAME="${0##*/}"

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

main() {
  local config=''
  local -a passthrough=()

  while (($# > 0)); do
    case $1 in
      --config)
        if (($# < 2)); then
          err "--config requires a path"
          return 64
        fi
        config=$2
        shift 2
        ;;
      --config=*)
        config=${1#--config=}
        shift
        ;;
      --)
        shift
        passthrough+=("$@")
        break
        ;;
      *)
        passthrough+=("$1")
        shift
        ;;
    esac
  done

  if [[ -n ${config} ]]; then
    # Fail closed: a missing or unreadable config should stop startup, not be skipped.
    if [[ ! -f ${config} || ! -r ${config} ]]; then
      err "config file not readable: ${config}"
      return 66
    fi
    passthrough=(--config "${config}" "${passthrough[@]}")
  fi

  # exec so the app becomes PID 1 and receives SIGTERM from `docker stop` directly.
  exec python -m app "${passthrough[@]}"
}

main "$@"
```

How it behaves:
- The other arguments are kept in an array and passed through exactly as given. Nothing is re-parsed by the shell.
- `--` ends option parsing, so the app can get its own `--config` if it needs one.
- A missing path or an unreadable config file exits non-zero with a message to stderr.
- It doesn't need a cleanup trap because it creates no temp files and `exec` replaces the shell.

The `Dockerfile` would also change. `CMD ["python", "-m", "app"]` would become `ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]`, and the file would need to be executable when it's copied in.

Separately, `scripts/backup.sh` has real problems I didn't touch:
- It doesn't use strict mode.
- Its variables aren't quoted.
- Its temp directory name, `/tmp/backup.$$`, can be guessed in advance.
- It has no cleanup trap, so a failed `scp` leaves the archive behind.

Tell me which config option you want (and whether to fix `backup.sh` too). In a session that can edit and run commands, I'll write the files, then run `shellcheck`, `bash -n`, and a test run that includes the failure cases.
