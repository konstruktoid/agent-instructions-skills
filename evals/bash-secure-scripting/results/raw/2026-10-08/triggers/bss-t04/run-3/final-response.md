I didn't change anything, because there's no entrypoint script in this repository. The `Dockerfile` has no `ENTRYPOINT`; it only runs `CMD ["python", "-m", "app"]`. Nothing in `docker-compose.yml`, `k8s/deployment.yml` or the CI files sets an entrypoint or command either. The only shell script in the repo is `scripts/backup.sh`, which has nothing to do with the container. I also can't create or edit files in this session.

Below is a proposed script you can add, followed by the `Dockerfile` change it needs.

**`docker-entrypoint.sh`** (proposed):

```bash
#!/usr/bin/env bash
#
# Container entrypoint: accept --config PATH, pass every other argument to the app.

set -Eeuo pipefail
shopt -s inherit_errexit

readonly PROGNAME="${0##*/}"
readonly DEFAULT_CONFIG='/app/config.yaml'

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

usage() {
  printf 'usage: %s [--config PATH] [--] [APP_ARGS...]\n' "${PROGNAME}" >&2
}

main() {
  local config="${APP_CONFIG:-${DEFAULT_CONFIG}}"
  local -a passthrough=()

  while (($# > 0)); do
    case "$1" in
      --config)
        if (($# < 2)); then
          err '--config requires a path'
          usage
          return 64
        fi
        config="$2"
        shift 2
        ;;
      --config=*)
        config="${1#--config=}"
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

  if [[ -z ${config} ]]; then
    err 'config path is empty'
    return 64
  fi
  if [[ ! -f ${config} || ! -r ${config} ]]; then
    err "config file not readable: ${config}"
    return 66
  fi

  export APP_CONFIG="${config}"
  # exec so the app becomes PID 1 and gets SIGTERM directly from the runtime.
  exec python -m app "${passthrough[@]}"
}

main "$@"
```

**`Dockerfile`:**

```dockerfile
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
```

You have to replace the existing `CMD ["python", "-m", "app"]`. Once there's an `ENTRYPOINT`, Docker passes `CMD` to it as arguments, so leaving the old line in would hand `python -m app` to your app as its arguments.

**How it behaves:**
- **Usage:** `docker run img --config /etc/app.yaml --verbose` and `docker run img --config=/etc/app.yaml -- --config x` both work. After `--`, everything is passed to the app untouched, including a literal `--config`.
- **No shell re-parsing:** arguments go through an array, so nothing runs them through the shell a second time. There's also no `eval`, which keeps arguments from being injected into a command.
- **Bad input:** a missing or empty path, or a file that can't be read, makes the script exit with an error on stderr. It exits 64 for bad usage and 66 for an unreadable file, and the app is never started.
- **No cleanup needed:** the script makes no temporary files, so it has no cleanup traps. `exec` also hands signals straight to the app.

**Assumptions to confirm:**
1. **How the app reads the path:** I couldn't see the app's code, so the script exports `APP_CONFIG`. If the app takes a `--config` flag instead, change the last line to `exec python -m app --config "${config}" "${passthrough[@]}"`.
2. **Default config path:** `/app/config.yaml` and falling back to an existing `APP_CONFIG` variable are both guesses.
3. **Where the script belongs:** I don't know which project this container is for, so I've used the repo root.

**Not verified:** I couldn't run `shellcheck`, `bash -n` or a build of the image here, so none of this has been tested. Before merging, run `shellcheck docker-entrypoint.sh` and `bash -n docker-entrypoint.sh`. Then try one valid run, plus one run with `--config` and no path, and check the exit codes.

If you can enable file editing, or tell me where the real entrypoint lives, I'll apply this and run those checks.
