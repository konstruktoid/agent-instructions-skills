I couldn't make this change, because the repository has no container entrypoint script. Nothing was edited and nothing was run.

**What's there now:**
- `Dockerfile` has no `ENTRYPOINT`. It ends with `CMD ["python", "-m", "app"]`.
- No file in the workspace mentions "entrypoint". The only shell script is `scripts/backup.sh`, which is a backup job.
- The `CMD` runs a module called `app`, but the only Python package I found is `src/ledger/`. The `Dockerfile` also installs from `requirements.txt`, which doesn't exist. So the image may not build or run as it stands.

I also can't write or run files in this session: I only have read and search tools. So I can't create the script or check it with `shellcheck`, `bash -n` or a test run. Here's a draft for you to review:

```bash
#!/usr/bin/env bash
#
# Container entrypoint: accepts --config PATH, passes all other arguments to the app.

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
      err "config file not readable: ${config}"
      return 66
    fi
    export APP_CONFIG="${config}"
  fi

  # exec makes the app PID 1, so it receives SIGTERM directly from the runtime.
  exec python -m app "${passthrough[@]}"
}

main "$@"
```

The matching `Dockerfile` change:

```dockerfile
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD []
```

How the draft behaves:
- **Passing arguments through:** everything except `--config` goes to the app as separate, quoted arguments, never as one rebuilt string. After `--`, everything is passed through as-is, including a literal `--config`.
- **Bad input:** a missing or empty config path exits with status 64, and an unreadable file exits with 66. In both cases the error goes to stderr before the app starts.
- **No cleanup needed:** the script creates no temporary files.

**Decisions for you:**
1. **Where should the script live,** and is there an existing one somewhere else that I should edit instead?
2. **How should the app get the config path?** The draft sets an `APP_CONFIG` environment variable, but I guessed that name. It could instead pass `--config` on to the app, or copy the file to a fixed location.
3. **What should the app command be?** `python -m app` doesn't match the code in the repo.

Once you've answered these and I can write files, I'll add the script and update the `Dockerfile`. Then I'll run `shellcheck`, `bash -n`, a normal run and the failure cases.
