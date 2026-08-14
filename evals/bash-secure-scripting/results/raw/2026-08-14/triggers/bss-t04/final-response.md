I don't have file-write or shell-execution tools available in this session (only Read/Glob/Grep/Skill), so I can't create or edit files directly. Here's the entrypoint script and the Dockerfile change for you to apply:

**`scripts/entrypoint.sh`** (new file):
```bash
#!/usr/bin/env bash
#
# Container entrypoint: parses --config, passes the rest through to the app.

set -Eeuo pipefail
shopt -s inherit_errexit

readonly PROGNAME="${0##*/}"

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

main() {
  local config=''
  local -a rest=()

  while (($#)); do
    case "$1" in
      --config)
        if (($# < 2)); then
          err "--config requires a value"
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
        rest+=("$@")
        break
        ;;
      *)
        rest+=("$1")
        shift
        ;;
    esac
  done

  if [[ -n ${config} ]]; then
    if [[ ! -f ${config} ]]; then
      err "config file not found: ${config}"
      return 66
    fi
    export APP_CONFIG="${config}"
  fi

  exec python -m app "${rest[@]}"
}

main "$@"
```

**`Dockerfile`** change: add `COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh` and `RUN chmod +x /usr/local/bin/entrypoint.sh`, then replace `CMD ["python", "-m", "app"]` with:
```
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD []
```

Key points: strict mode, `--config`/`--config=VALUE` both handled, `--` stops option parsing, unknown args pass through in `rest[@]`, config path is validated to exist before use, and `exec` replaces the shell process so signals reach the app directly (important as PID 1 in a container).

If you'd like me to actually write these files, please grant me file-write access (Edit/Write tools) or a shell tool, and I'll apply them and run `shellcheck`/`bash -n` to verify.
