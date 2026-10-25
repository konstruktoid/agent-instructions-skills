I couldn't make this change. The repo has no container entrypoint script, and this session can't create or edit files or run commands. I can only read and search.

**What the repo has:**
- `Dockerfile` has no `ENTRYPOINT`. It runs the app directly with `CMD ["python", "-m", "app"]`.
- `scripts/backup.sh` is a backup job, not an entrypoint. It's also not safe as written (no strict mode, unquoted variables, a predictable `/tmp/backup.$$`, and no cleanup if it fails partway). That's worth fixing separately.

**Here's a draft you could add as `docker-entrypoint.sh`.** I haven't run `shellcheck`, `bash -n` or the script itself on it, so treat it as untested:

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

main() {
  local config=''
  local config_set=0
  local -a passthrough=()

  while (($# > 0)); do
    case "$1" in
      --config)
        if (($# < 2)); then
          err "--config requires a path"
          return 64
        fi
        config="$2"
        config_set=1
        shift 2
        ;;
      --config=*)
        config="${1#--config=}"
        config_set=1
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

  if ((config_set)); then
    if [[ -z ${config} || ! -f ${config} || ! -r ${config} ]]; then
      err "config file missing or unreadable: ${config}"
      return 66
    fi
    export APP_CONFIG="${config}"
  fi

  # exec so python runs as PID 1 and gets SIGTERM from `docker stop` directly.
  exec python -m app "${passthrough[@]}"
}

main "$@"
```

The `Dockerfile` would need these changes:
```dockerfile
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
```
The old `CMD ["python", "-m", "app"]` has to go. Otherwise those words get passed through to the app as arguments.

**How the draft behaves:**
- It accepts both `--config PATH` and `--config=PATH`.
- It stops with an error if `--config` has no value, or if the path doesn't point to a readable file.
- Everything else, and anything after `--`, goes to the app unchanged and in order.

**One thing you need to decide:** I don't know how the app reads its config, so the draft passes the path in an environment variable called `APP_CONFIG`. If the app takes a `--config` flag instead, change the last step to `exec python -m app --config "${config}" "${passthrough[@]}"` (and run that only when `--config` was given). Tell me which it is, and enable file editing and shell access if you'd like me to add the script, update the `Dockerfile`, and test it properly.
