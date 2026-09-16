Files changed: `bin/mkuser-config.sh` (refactored into `main`/`err` with a source-guard, rejects empty `--name` with a stderr message and exit 1), `bin/mkuser-config_test.sh` (new, covers the rejection and a happy-path regression check), `README.md` (dropped the now-inaccurate "only lib/ is covered" line). Verified: `bash -n` and `shellcheck -x` clean on both scripts, `make test` passes, and the new test was confirmed to fail against both the original script and an intermediate version with the guard but no validation.

/clear before starting anything unrelated.
