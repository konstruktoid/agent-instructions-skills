I couldn't make this change. There's no entrypoint script in the repo, and I only have read and search tools here, so I couldn't create files or run anything.

The container currently starts like this (`Dockerfile:5`), with no `ENTRYPOINT` and no shell script involved:

```dockerfile
CMD ["python", "-m", "app"]
```

The only shell script is `scripts/backup.sh`, which isn't used by the image.

Here's a draft you could add as `docker-entrypoint.sh`. It's untested: I haven't run `shellcheck`, `bash -n` or the script itself.

```bash
#!/usr/bin/env bash
#
# Container entrypoint: accept --config PATH, pass every other argument to the app.

set -Eeuo pipefail
shopt -s inherit_errexit

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
          err '--config requires a path'
          return 64
        fi
        config="$2"
        shift 2
        ;;
      --config=*)
        config="${1#--config=}"
        if [[ -z ${config} ]]; then
          err '--config requires a path'
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

  # exec so the app replaces this shell as PID 1 and receives SIGTERM directly.
  exec python -m app "${passthrough[@]}"
}

main "$@"
```

And the `Dockerfile` change:

```dockerfile
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
```

How it behaves:
- **Two forms:** it accepts both `--config PATH` and `--config=PATH`. If no path is given it stops with exit code 64; if the file is missing or unreadable it stops with 66.
- **Passing arguments through:** everything else goes to the app unchanged, kept as a list so arguments are never re-read as shell code. Anything after `--` is passed through as-is, even a literal `--config`.
- **No temp files:** it creates none, so it needs no cleanup on exit.

Decisions for you:
1. **How the app gets the config path.** I don't know how the app reads its config, so I assumed an `APP_CONFIG` environment variable. If the app takes its own `--config` flag instead, replace the `export` with `passthrough=(--config "${config}" "${passthrough[@]}")`.
2. **What the extra arguments run.** Here they go to `python -m app`. The other common pattern is `exec "$@"`, which runs whatever command you pass. That's more flexible, but `docker run image bash` would then skip the app entirely.
3. **Signal handling.** Since `exec` makes Python the container's main process (PID 1), use `docker run --init` (or `init: true` in `docker-compose.yml`) if the app doesn't handle SIGTERM itself.

Once you've written the file, run:

```
shellcheck docker-entrypoint.sh && bash -n docker-entrypoint.sh
docker build -t app-test . && docker run --rm app-test --config /nonexistent; echo $?   # expect 66
```

If you can give me write and shell access, I can add the files and run these checks myself.
