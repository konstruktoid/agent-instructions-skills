I couldn't make this change: there's no container entrypoint script in the repo, and this session can't write files.

**What's there now**
- `Dockerfile:5` runs the app directly with `CMD ["python", "-m", "app"]`. There's no `ENTRYPOINT` and no wrapper script.
- The only shell script is `scripts/backup.sh`, which is a backup job, not an entrypoint.

This session only gave me read, search and skill tools, so I couldn't create the file or run `shellcheck`, `bash -n` or the script itself. Below is a proposed version. **It hasn't been linted or run.**

**Proposed `docker-entrypoint.sh`**

```bash
#!/usr/bin/env bash
#
# Container entrypoint: accept --config PATH, pass all other arguments to the app.

set -Eeuo pipefail
shopt -s inherit_errexit

readonly PROGNAME="${0##*/}"
readonly DEFAULT_CONFIG='/app/config.yaml'

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

usage() {
  printf 'usage: %s [--config PATH] [--] [ARGS...]\n' "${PROGNAME}" >&2
}

main() {
  local config="${APP_CONFIG:-${DEFAULT_CONFIG}}"
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

  # Fail closed: a missing or unreadable config is an error, not a silent default.
  if [[ ! -f ${config} || ! -r ${config} ]]; then
    err "config file not readable: ${config}"
    return 66
  fi

  # exec makes the app PID 1, so it receives SIGTERM from `docker stop` directly.
  exec python -m app --config "${config}" "${passthrough[@]}"
}

main "$@"
```

**`Dockerfile` change**

```dockerfile
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod 0755 /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
```

You need to replace `CMD ["python", "-m", "app"]`. If you keep it, those words get passed to the app as extra arguments.

**How it works**
- **Arguments:** it accepts `--config PATH` and `--config=PATH`. Everything else is kept in order and passed to the app unchanged. Anything after `--` is passed through even if it looks like `--config`.
- **Safety:** arguments are only ever stored in an array and quoted when used, so nothing is re-read as shell code.
- **Exit codes:** a missing path value exits 64, and a config file that's missing or unreadable exits 66.

**Assumptions to check**
- **The app takes `--config`:** I couldn't see how the app reads its config. If it uses an environment variable instead, change the `exec` line to something like `APP_CONFIG="${config}" exec python -m app "${passthrough[@]}"`.
- **The fallback config:** `APP_CONFIG` and `/app/config.yaml` are placeholders I made up. Swap in your real default.
- **Bash version:** the empty-array expansion needs Bash 4.4 or later. The Bash in `python:3.13-slim` should be newer than that.

**To verify once the file exists**
- Run `shellcheck docker-entrypoint.sh` and `bash -n docker-entrypoint.sh`.
- Run `docker run IMAGE --config /path a b` and check the app gets `a b`.
- Run `docker run IMAGE --config` and check it exits 64.

Separately, I noticed `scripts/backup.sh` has no strict mode, no quoting, a temporary directory under `/tmp` with a guessable name, and cleanup that's skipped if anything fails. I haven't changed it; I can harden it if you'd like.
