I couldn't make this change. There's no entrypoint script in the repository, and I don't have file-editing or shell tools in this session, so I couldn't create one or run it. Here's what's there now:

- `Dockerfile` has no `ENTRYPOINT`. It just runs `CMD ["python", "-m", "app"]`.
- The only shell script is `scripts/backup.sh`, which is a nightly backup job, not an entrypoint.

Here is a draft you could add as `docker-entrypoint.sh`. It hasn't been run or checked with `shellcheck`.

```bash
#!/usr/bin/env bash
#
# Container entrypoint: accept --config PATH, pass all other arguments to the app.

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
          err "--config requires a path"
          usage
          return 64
        fi
        config="$2"
        shift 2
        ;;
      --config=*)
        config="${1#--config=}"
        if [[ -z ${config} ]]; then
          err "--config requires a path"
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
      err "config file not found or not readable: ${config}"
      return 66
    fi
    export APP_CONFIG="${config}"
  fi

  # exec so the app runs as PID 1 and receives SIGTERM from `docker stop`.
  exec python -m app "${passthrough[@]}"
}

main "$@"
```

And the matching `Dockerfile` change:

```dockerfile
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
```

`CMD` has to change. With an `ENTRYPOINT` in place, whatever is in `CMD` gets passed to it as arguments, so the current `CMD` would make the app receive `python -m app` as its own arguments.

**How it works:**
- **Forms accepted:** both `--config PATH` and `--config=PATH`. Everything after `--` is passed through untouched, even if it looks like `--config`.
- **Errors:** a missing path or an unreadable file stops startup with exit code 64 or 66 instead of starting the app.
- **No re-parsing:** arguments are collected in an array and expanded with quotes. Nothing goes through `eval` or `bash -c`.
- **Bash version:** an empty argument list combined with `set -u` needs Bash 4.4 or later. `python:3.13-slim` ships Bash 5.

**Assumptions to check:**
1. **How the app gets the config path.** The draft sets it in an `APP_CONFIG` environment variable, which is a name I made up. If the app takes the path as its own flag, use `exec python -m app --config "${config}" "${passthrough[@]}"` instead.
2. **The file name and location.** If you meant a different script, or one that isn't committed yet, tell me where it is.

Once I have file-editing and shell access, I can add these files and run `shellcheck`, `bash -n`, and both a passing and a failing case.
