`bin/prune-artifacts.sh` now fails loudly when the directory doesn't exist. I haven't committed anything.

- **Missing directory:** it prints `prune-artifacts: directory not found: <path>` to stderr and exits 1. It no longer prints the "pruned …" success line. Cron will now report the failure.
- **`find` errors:** a failure inside `find` now also makes the script exit nonzero. Before, it would have printed "pruned" regardless.

I added `tests/prune-artifacts.test.sh`, which uses temp directories. It covers these cases:
- A missing directory exits nonzero, names the path on stderr, and prints no success message.
- An existing directory exits 0, deletes the old archive and keeps the new one.
- An empty directory exits 0.

All 7 checks pass with the fix. I also stashed the script change and re-ran the tests against the original script. The three missing-directory checks failed there and the other four passed, so the tests do detect the bug.

I also replaced the README line saying there are no tests with a note about the new exit behavior and the test script.

If you deploy this change, the first cron run with a bad path will now fail instead of passing silently. If your cron setup doesn't send mail or alert on failures, you'll still need that for the failure to be noticed.
