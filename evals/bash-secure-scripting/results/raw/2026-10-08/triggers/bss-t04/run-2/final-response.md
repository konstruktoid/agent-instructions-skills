I couldn't make this change, for two reasons:

1. **There's no entrypoint script in this repo.** The `Dockerfile` has no `ENTRYPOINT`, only `CMD ["python", "-m", "app"]`. I searched the workspace for "entrypoint" and found nothing, so there was nothing to edit. The only shell script is `scripts/backup.sh`.
2. **I have no way to write files or run commands in this session.** I can only read and search, so I couldn't create the script, update the `Dockerfile`, or run `shellcheck`, `bash -n` or the script itself.

Here's a draft you can add as `docker-entrypoint.sh`. I haven't run or checked it at all:

```bash
#!/usr/bin/env bash
#
# Container entrypoint: accept --config PATH, pass the remaining arguments to the app.

set -Eeuo pipefail
shopt -s inherit_errexit

readonly PROGNAME="${0##*/}"

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

usage() {
  printf 'usage: %s [--config PATH] [--] [ARGS...]\n' "${PROGNAME}" >&2
}

main() {
  local config=''
  local -a passthrough=()

  while (($# > 0)); do
    case "$1" in
      --config)
        if (($# < 2)) || [[ -z $2 ]]; then
          err '--config requires a path'
          usage
          return 64
        fi
        config="$2"
        shift 2
        ;;
      --config=*)
        config="${1#--config=}"
        if [[ -z ${config} ]]; then
          err '--config requires a path'
          usage
          return 64
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
      err "config file not readable: ${config}"
      return 66
    fi
    export APP_CONFIG="${config}"
  fi

  # exec so the app runs as PID 1 and receives the container's signals directly.
  exec python -m app "${passthrough[@]}"
}

main "$@"
```

And these `Dockerfile` changes:

```dockerfile
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
```

Notes on the draft:
- **One guess to check:** I don't know how the app reads its config, so the script puts the path in an `APP_CONFIG` environment variable. If the app takes its own `--config` flag instead, put `--config "${config}"` at the start of the `exec` arguments.
- **Pass-through:** every argument the script doesn't recognise goes to the app unchanged. Anything after `--` is passed as-is, even if it looks like `--config`.
- **Failures:** a missing value or an unreadable config file prints a message to stderr and exits non-zero (64 or 66) before the app starts.
- **`CMD` change:** once there's an `ENTRYPOINT`, Docker passes `CMD` to the script as arguments. The script already runs `python -m app`, so `CMD` has to be emptied, or the app would receive `python -m app` as its arguments.
- **Bash version:** expanding an empty `"${passthrough[@]}"` under `set -u` needs Bash 4.4 or later. `python:3.13-slim` is Debian-based and should meet that, but I haven't confirmed it.

Before merging, run `shellcheck docker-entrypoint.sh` and `bash -n docker-entrypoint.sh`. Then build the image and try three runs: one with `--config` pointing at a real file plus extra arguments, one with `--config` and no path, and one with a path that doesn't exist. Check the exit status of each. If you give me write and shell access, I can add the files and run these checks myself.
