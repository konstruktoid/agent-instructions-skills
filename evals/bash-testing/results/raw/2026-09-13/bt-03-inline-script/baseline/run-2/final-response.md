Verified via `make test` (exit 0, both tests pass).

Files changed: `bin/mkuser-config.sh` (rejects empty `--name` with exit 64 and a stderr message before touching the output file), `bin/mkuser-config_test.sh` (new — covers the rejection: non-zero exit, error message, no file created), `README.md` (dropped the now-stale "only lib/ is covered" note).

/clear before starting anything unrelated.
