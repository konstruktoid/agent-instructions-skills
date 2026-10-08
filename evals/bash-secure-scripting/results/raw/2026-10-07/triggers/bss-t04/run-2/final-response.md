I couldn't create or edit any files. Write is disabled in this session, and I have no Edit or Bash tool. Nothing is on disk, so none of it has been through shellcheck, `bash -n` or a test run.

The repo also has no container entrypoint script to modify. The Dockerfile runs `CMD ["python", "-m", "app"]` directly, and `scripts/backup.sh` is a backup job. So I wrote a new one. Nothing in the repo reads a config setting yet, so I chose to export `APP_CONFIG`. Tell me if the app expects something else, such as a `--config` flag passed on to it.

If you want it, save this as `scripts/entrypoint.sh`:

```bash
#!/usr/bin/env bash
#
# Container entrypoint: consume --config PATH, pass every other argument through.

set -Eeuo pipefail
shopt -s inherit_errexit

PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH

readonly PROGNAME="${0##*/}"

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

main() {
  local config=''
  local -a passthrough=()

  while (($# > 0)); do
    case "$1" in
      --config)
        if (($# < 2)) || [[ -z $2 ]]; then
          err "--config requires a path"
          return 64
        fi
        config="$2"
        shift 2
        ;;
      --config=*)
        config="${1#--config=}"
        if [[ -z ${config} ]]; then
          err "--config requires a path"
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
      err "config file not found or unreadable: ${config}"
      return 66
    fi
    export APP_CONFIG="${config}"
  fi

  if ((${#passthrough[@]} == 0)); then
    err "no command given"
    return 64
  fi

  exec "${passthrough[@]}"
}

main "$@"
```

It handles arguments like this:
- **Accepted forms:** it takes `--config PATH` and `--config=PATH`.
- **Pass-through:** every other argument goes through unchanged, and anything after `--` is never parsed.
- **Failures:** a missing or empty path exits 64, an unreadable file exits 66, and an empty command exits 64. All of them report to stderr.

To wire it in, change the end of the Dockerfile to:

```dockerfile
ENTRYPOINT ["bash", "/app/scripts/entrypoint.sh"]
CMD ["python", "-m", "app"]
```

With that change, `docker run img --config /etc/app.toml` would replace `CMD` and fail with "no command given". The user would have to write `docker run img --config /etc/app.toml python -m app`. To make `--config` alone work, the script should append the default `python -m app` when no command is given. Say if you want that.

If you enable Write, I can create both files, then run shellcheck, `bash -n`, and a success and a failure test.
