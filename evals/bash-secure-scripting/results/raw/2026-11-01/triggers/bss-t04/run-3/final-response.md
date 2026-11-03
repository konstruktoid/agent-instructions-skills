I couldn't make this change: the repository has no container entrypoint script, and I don't have file-write or shell tools in this session.

**What's there now:**
- `Dockerfile:5` starts the app directly with `CMD ["python", "-m", "app"]`. There's no `ENTRYPOINT` and no script for it to call.
- The only shell script is `scripts/backup.sh`, a nightly backup job, not an entrypoint.

**One thing I need from you:** how should the app receive the config path? I couldn't find any code that reads it. The two usual options are a `--config` flag passed on to `python -m app`, or an environment variable such as `APP_CONFIG`. The draft below passes it as a flag, so change that one line if it's the variable.

**Draft `docker-entrypoint.sh`.** This is untested; I haven't run shellcheck, `bash -n` or the script itself:

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
    passthrough=(--config "${config}" "${passthrough[@]}")
  fi

  # exec so the app runs as PID 1 and receives the container's stop signals directly.
  exec python -m app "${passthrough[@]}"
}

main "$@"
```

And in the `Dockerfile`, replace line 5 with:

```dockerfile
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
```

**How it behaves:**
- **Both forms work:** `--config PATH` and `--config=PATH`.
- **Errors:** a missing or empty path exits with status 64 (a usage error). A config file that can't be read exits with 66 (missing input). Both print a message to stderr. The app never starts with a bad config.
- **Pass-through:** every other argument, and anything after `--`, goes to the app unchanged.
- **No re-parsing of input:** arguments are held in an array, so they never pass through `eval` or `bash -c`.
- **Bash version:** `"${passthrough[@]}"` with an empty array is safe under `set -u` from Bash 4.4. `python:3.13-slim` ships Bash 5.

**To finish it**, once you've told me how the app takes its config, either give me write and shell access or run these yourself:
- `shellcheck docker-entrypoint.sh`
- `bash -n docker-entrypoint.sh`
- Build the image and run it four ways: with no arguments, with `--config /nonexistent` (should exit 66), with a bare `--config` (should exit 64), and with a real config plus extra arguments.

**Separately, in `scripts/backup.sh`:** the script doesn't stop when a command fails, its variables are unquoted, and it uses a predictable `/tmp/backup.$$` directory that isn't removed if it exits early. I can fix that in another change if you'd like.
