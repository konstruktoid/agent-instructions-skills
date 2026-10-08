I couldn't find a container entrypoint script to change, so I haven't edited anything.

- **Dockerfile:** it has no `ENTRYPOINT`. It ends with `CMD ["python", "-m", "app"]`.
- **Shell scripts:** the only one is `scripts/backup.sh`, a nightly backup job that doesn't parse arguments and isn't referenced by the Dockerfile.
- **Other files:** there is no `.shellcheckrc`, `Makefile`, pre-commit config or `CLAUDE.md` to follow.

Do you want me to create a new `scripts/entrypoint.sh` and wire it into the Dockerfile? I'd write it as follows:

- **Parsing:** it accepts `--config PATH` and `--config=PATH`, and rejects a missing or empty value with exit status 64.
- **Pass-through:** everything else goes through unchanged via `exec "$@"`, and `--` ends option parsing.
- **Config path:** it checks that the file exists and is readable, then exports it as `APP_CONFIG`. If your app reads the path another way, such as `--config` on its own command line, tell me and I'll pass it that way instead.
- **Hardening:** it follows the repo's bash-secure-scripting skill, with `set -Eeuo pipefail`, a fixed `PATH`, and quoted expansions.
- **Dockerfile:** it gets `ENTRYPOINT ["/app/scripts/entrypoint.sh"]`, and `CMD` stays `["python", "-m", "app"]` as the default command.

Or if the entrypoint lives somewhere else, such as another branch or a different repo, point me to it.
