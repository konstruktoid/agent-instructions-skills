I couldn't make this change because the repository has no container entrypoint script.

- **`Dockerfile`** has no `ENTRYPOINT`. It only runs `CMD ["python", "-m", "app"]`.
- **No match anywhere:** searching every file for "entrypoint" (any capitalisation) found nothing.
- **The only shell script** is `scripts/backup.sh`, and nothing connects it to the container.

Also, my current tools can only read files and can't edit them or run commands. So even with a target I couldn't write the script or run the required checks (`shellcheck`, `bash -n`, and test runs on good and bad input).

**What I need from you:**
1. Which file you mean. It could be a script on another branch or path, or a new `docker-entrypoint.sh` that the `Dockerfile` would call through `ENTRYPOINT`.
2. Permission for me to edit files and run commands, so I can write the script and test it.

**What I'd write**, once both are sorted: a script that starts with `set -Eeuo pipefail` and reads `--config PATH` and `--config=PATH`. It would accept `--` to mark the end of its own options. It would check that the config path is a readable regular file and stop with an error if it isn't. It would pass everything else on unchanged with `exec "$@"`, which falls back to the image's `CMD` when nothing else is given. It would never use `eval` or build a command from a string. The `Dockerfile` would get `ENTRYPOINT ["/app/docker-entrypoint.sh"]` and keep its current `CMD`.

I still need to know how the app should receive the config. One option is setting an environment variable such as `APP_CONFIG`; the other is adding the path back into the command's arguments. Which one should I use?
