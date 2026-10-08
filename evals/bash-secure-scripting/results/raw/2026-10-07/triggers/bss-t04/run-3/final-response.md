I couldn't find a container entrypoint script to modify, so I haven't changed anything.

- **Dockerfile:** it has no `ENTRYPOINT`. It only sets `CMD ["python", "-m", "app"]`.
- **Shell scripts:** the only one in the repo is `scripts/backup.sh`, a nightly backup job. It isn't a container entrypoint, and `--config` doesn't fit it.
- **Search:** a grep for "entrypoint" (case-insensitive) matched nothing.

I also couldn't read the skill's reference files or `bash_coding_instructions.md`, because the read permission was denied. I'd want those before writing the script.

How would you like to proceed?

1. **Create a new `scripts/entrypoint.sh`.** I would also add `COPY` and `ENTRYPOINT ["/app/scripts/entrypoint.sh"]` lines to the Dockerfile, keeping `CMD ["python", "-m", "app"]` as the default. The script would:
   - parse `--config PATH`, also accepting `--config=PATH`
   - check that the path is non-empty and the file is readable
   - treat `--` as the end of options
   - `exec "$@"` with everything else, so the app runs as PID 1 and receives signals
   - pass the config to the app through an environment variable or an argument, which depends on how `app` reads it
2. **Use a different script.** If the entrypoint lives elsewhere, such as an untracked file or another branch, tell me the path.
3. **Change `backup.sh` instead.** I'd do this only if that's what you meant.

For option 1, I need to know how the app takes its config path. I don't know whether it uses a `--config` flag, a `CONFIG_PATH` variable, or something else.
