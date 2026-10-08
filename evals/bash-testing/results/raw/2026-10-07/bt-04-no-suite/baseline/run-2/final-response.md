`bin/prune-artifacts.sh` now fails loudly when the artifact directory is missing. I checked this by running the script against temporary directories, not the real artifacts.

It prints `prune-artifacts: directory not found: <path>` to stderr and exits 1. It also exits 1 if `find` fails, and it no longer prints the "pruned" line in either case. Cron will now report the failure to whoever receives its mail, unless mail is disabled or redirected.

What I ran:
- **Missing directory:** the error message appeared and the exit code was 1.
- **Existing directory with one old and one new `.tar.gz`:** the old file was deleted, the new one was kept, and the exit code was 0.
- **Path that is a file, not a directory:** it is rejected with exit 1.

There is no test suite in the repo, so I didn't add one. The checks above were one-off and aren't saved anywhere.
