I didn't change anything. The repository has no container entrypoint script, and this session only gives me read and search tools, so I can't create or edit files.

What I found:
- `Dockerfile` has no `ENTRYPOINT`. It ends with `CMD ["python", "-m", "app"]`.
- The only shell script is `scripts/backup.sh`, a nightly backup job, not an entrypoint.
- Nothing in the repo reads a config path yet (no `argparse`, `sys.argv` or `config` references in the app code).

So this has to be a new script. Here's one you can add as `docker-entrypoint.sh`. It accepts `--config PATH` or `--config=PATH`, checks the file, passes it to the app as `APP_CONFIG`, and hands every other argument to the app unchanged:

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
  printf 'usage: %s [--config PATH] [--] [APP_ARGS...]\n' "${PROGNAME}" >&2
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
      err "config file not found or not readable: ${config}"
      return 66
    fi
    export APP_CONFIG="${config}"
  fi

  # exec so the app becomes PID 1 and gets SIGTERM from `docker stop` directly.
  exec python -m app "${passthrough[@]}"
}

main "$@"
```

And in the `Dockerfile`, replace the `CMD` line with:

```dockerfile
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
```

Then `docker run IMAGE --config /etc/app/app.toml --verbose` runs `python -m app --verbose` with `APP_CONFIG=/etc/app/app.toml` set.

Some notes on the design:
- **`exec` with an array:** passed-through arguments are never re-read as shell code, and the app receives `docker stop` signals itself. That's why the script has no traps.
- **Parsing order:** if `--config` is given more than once, the last one wins. Anything after `--` goes to the app untouched, even if it's another `--config`.
- **Exit codes:** a missing value exits 64 and a missing or unreadable file exits 66, so a bad mount fails at startup instead of later inside the app.

**Decision for you:** the app doesn't read any config yet, so I passed the path as the `APP_CONFIG` environment variable. If you'd rather the app get it as its own `--config` argument, change the `export` line to `passthrough=(--config "${config}" "${passthrough[@]}")`.

None of this has been tested. Before merging, run `shellcheck` and `bash -n` on the script, then try `--config` with a real file, with a missing file, and with no value. If you give me edit and shell access, I can add the files and run those checks myself.
