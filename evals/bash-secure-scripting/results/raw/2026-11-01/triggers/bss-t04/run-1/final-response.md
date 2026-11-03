I didn't make the change, for two reasons:

1. **There's no container entrypoint in this workspace.** No file is named `*entrypoint*`, and no file mentions `ENTRYPOINT`. There's no Dockerfile either. The only shell script is `scripts/backup.sh`, which is a nightly backup job, not an entrypoint.
2. **I can't edit files in this session.** I only have read and search tools, so I can't write files or run `shellcheck`/`bash -n`.

Here's a draft you could drop in as e.g. `docker/entrypoint.sh`. I haven't run or linted it.

```bash
#!/usr/bin/env bash
#
# Container entrypoint: accepts an optional --config PATH and execs the rest.

set -Eeuo pipefail
shopt -s inherit_errexit

readonly PROGNAME="${0##*/}"

err() { printf '%s: %s\n' "${PROGNAME}" "$*" >&2; }
usage() { printf 'usage: %s [--config PATH] [--] COMMAND [ARGS...]\n' "${PROGNAME}" >&2; }

main() {
  local config=''
  local -a passthrough=()

  while (($# > 0)); do
    case $1 in
      --config)
        if (($# < 2)) || [[ -z $2 || $2 == -* ]]; then
          err '--config requires a path'; usage; return 64
        fi
        config=$2
        shift 2
        ;;
      --config=*)
        config=${1#--config=}
        if [[ -z ${config} ]]; then
          err '--config requires a path'; usage; return 64
        fi
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
    if [[ ! -f ${config} || ! -r ${config} ]]; then
      err "config file not readable: ${config}"; return 66
    fi
    export APP_CONFIG="${config}"   # or pass it to the app as a flag
  fi

  if ((${#passthrough[@]} == 0)); then
    err 'no command given'; usage; return 64
  fi

  # exec so the app becomes PID 1 and receives the signals the container sends.
  exec "${passthrough[@]}"
}

main "$@"
```

- **Pass-through:** the arguments are kept in an array and run with `exec "${passthrough[@]}"`. They're never joined into a string or passed to `eval`, so they can't be used to inject shell commands.
- **Errors:** a missing or empty `--config` value fails with exit 64, and a config file that can't be read fails with exit 66.
- **No cleanup traps:** because of `exec`, the script is replaced by the app, so it needs none.

I need two things from you to finish:
- **Where the entrypoint is:** its path, or the repo or branch where it lives (if it's somewhere other than this workspace).
- **How the app should receive the config:** an environment variable (`APP_CONFIG` above is a placeholder), a flag added to the command, or a default command when none is given.

Once I have a session that can edit files, I can make the change and run `shellcheck`, `bash -n`, and a test on both a working and a failing input.

Separately, `scripts/backup.sh` has real problems:
- It has no strict mode.
- Every variable is unquoted.
- Its temporary directory is a predictable `/tmp/backup.$$` instead of one made with `mktemp`.
- Nothing cleans that directory up if `tar` or `scp` fails.

I can harden it too if you'd like.
