I couldn't make this change yet, because the repository has no entrypoint script. It has two shell-related files:

- `Dockerfile`, which has no `ENTRYPOINT` and runs `CMD ["python", "-m", "app"]` directly.
- `scripts/backup.sh`, a nightly backup script, not an entrypoint.

I also can't write files or run commands in this session, so I can't create the script or run `shellcheck` and `bash -n` on it. Below is a draft for you to add, as `docker-entrypoint.sh` at the repository root. I haven't linted, run or tested it.

```bash
#!/usr/bin/env bash
#
# Container entrypoint: accepts an optional --config PATH, then runs the app
# with every other argument passed through unchanged.

set -Eeuo pipefail
shopt -s inherit_errexit

readonly PROGNAME="${0##*/}"

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

usage() {
  printf 'usage: %s [--config PATH] [--] [ARG...]\n' "${PROGNAME}" >&2
}

main() {
  local config=''
  local -a passthrough=()

  while (($# > 0)); do
    case $1 in
      --config)
        if (($# < 2)) || [[ -z $2 ]]; then
          err '--config requires a path'
          usage
          return 64
        fi
        config=$2
        shift 2
        ;;
      --config=*)
        config=${1#--config=}
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
    # How the app receives the path is an assumption; see the notes below.
    export APP_CONFIG="${config}"
  fi

  # exec makes the app PID 1, so it receives SIGTERM directly from `docker stop`.
  exec python -m app "${passthrough[@]}"
}

main "$@"
```

And the `Dockerfile` change:

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt \
 && chmod 0755 /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD []
```

With that in place, `docker run IMAGE --config /etc/app.toml --verbose` runs `python -m app --verbose` with `APP_CONFIG=/etc/app.toml`. Anything after `--` is passed through as-is, even if it's another `--config`.

**How the script behaves:**
- Arguments are kept in an array and never re-parsed by the shell, so nothing can inject a command.
- A missing or empty `--config` value exits with code 64. A config file that doesn't exist or can't be read exits with 66. Both print an error to stderr.
- `exec` replaces the shell with Python, so there's nothing to clean up and signals go straight to the app.

**Questions for you:**
1. **How should the app receive the config path?** I don't know how `app` reads its config, so I used an `APP_CONFIG` environment variable. If the app takes its own flag instead, change the `exec` line to `exec python -m app --config "${config}" "${passthrough[@]}"`, adding it only when `config` is set.
2. **Script location and name:** I picked `docker-entrypoint.sh` at the root. Change both if you'd prefer it under `scripts/`.

**To check after you add it:** run `shellcheck docker-entrypoint.sh` and `bash -n docker-entrypoint.sh`. Then try one normal run plus three failure cases: `--config` with no value, `--config=`, and a path that doesn't exist. Each failure should exit non-zero (64 or 66).

**Separate problem in `scripts/backup.sh`:** it has no strict mode, so a failed `tar` still gets copied by `scp`. Its variables are unquoted, its temp directory under `/tmp` has a predictable name, and it only cleans up if every step succeeds. I can harden it if you'd like.
