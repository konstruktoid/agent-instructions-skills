I couldn't make this change: this repository has no container entrypoint script, and I don't have file-writing or shell tools in this session.

What's here:
- **`Dockerfile`** has no `ENTRYPOINT`. It runs `CMD ["python", "-m", "app"]` directly.
- **`scripts/backup.sh`** is the only shell script, and it's a nightly backup job, not an entrypoint.
- Nothing in the repo reads a config path. A search for `--config`, `argparse` and `CONFIG` found nothing, so I don't know how the app expects to receive one.

Below is a draft `docker-entrypoint.sh` you could add. It hasn't been run or checked with `shellcheck`. I've assumed it should hand the config to the app through an `APP_CONFIG` environment variable; if the app should get `--config` as an argument instead, only the `export` line changes.

```bash
#!/usr/bin/env bash
#
# Container entrypoint: accept an optional --config PATH, then exec the
# remaining arguments (default: the app) as PID 1.

set -Eeuo pipefail
shopt -s inherit_errexit

readonly PROGNAME="${0##*/}"

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

usage() {
  printf 'usage: %s [--config PATH] [--] [COMMAND [ARG...]]\n' "${PROGNAME}" >&2
}

main() {
  local config=''

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
          return 64
        fi
        shift
        ;;
      --)
        shift
        break
        ;;
      *)
        # First unrecognised argument: everything from here is passed through.
        break
        ;;
    esac
  done

  if [[ -n ${config} ]]; then
    if [[ ! -f ${config} || ! -r ${config} ]]; then
      err "config is not a readable regular file: ${config}"
      return 66
    fi
    export APP_CONFIG="${config}"
  fi

  if (($# == 0)); then
    set -- python -m app
  fi

  # exec so the command becomes PID 1 and receives the container's signals directly.
  exec "$@"
}

main "$@"
```

The `Dockerfile` would then need:

```dockerfile
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "-m", "app"]
```

How it behaves:
- **Passthrough:** parsing stops at the first argument it doesn't recognise, or at `--`. Everything after that is run untouched with `exec "$@"`. Arguments are never put into a string or run through `eval`.
- **Signals:** because of `exec`, the app replaces the shell as PID 1. `docker stop` then reaches the app directly, and no trap is needed because the script makes no temp files.
- **Bad input fails:** a missing or empty `--config` value exits with 64, and a path that isn't a readable file exits with 66. Both print to stderr.

To finish, someone with write access needs to add the file and update the `Dockerfile`. Then run `shellcheck` and `bash -n` on it, and test these cases with their exit codes:
- no arguments
- `--config` with a valid file
- `--config` with no value
- `--config` pointing at a missing file
- `-- some-cmd --config x`, which should pass `--config x` through to the command

Separately, `scripts/backup.sh` has real problems. Its paths aren't quoted, it uses a predictable `/tmp/backup.$$` directory, and it has no strict mode. It also has no cleanup trap, so a failed `tar` or `scp` leaves the directory behind. Can you confirm two things: should the config go to the app as `APP_CONFIG` or as an argument? And do you want `backup.sh` hardened as well?
