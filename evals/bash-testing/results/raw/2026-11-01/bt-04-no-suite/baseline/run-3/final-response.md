`bin/prune-artifacts.sh` now fails loudly when the artifact directory doesn't exist. It prints `error: artifact directory not found: <dir>` to stderr and exits 1, and it no longer prints the "pruned …" line in that case. A failure from `find` itself is also propagated now.

I ran it against four cases:
- **Missing directory:** it printed the error and exited 1.
- **Existing directory:** I put a 30-day-old `.tar.gz` and a fresh one in a temp directory. It deleted only the old one, printed the "pruned" line and exited 0.
- **Default `artifacts` from the repo root:** it exited 0.
- **Default `artifacts` from a different working directory:** it exited 1, because the default path is relative.

The default path is relative to the working directory, so a crontab entry should pass an absolute path or `cd` into the right directory first. Otherwise it will now fail every night, which is the intended behaviour.

I didn't add a test file, since the repo has no test setup. I checked these cases by hand, and the temp directory is cleaned up.
