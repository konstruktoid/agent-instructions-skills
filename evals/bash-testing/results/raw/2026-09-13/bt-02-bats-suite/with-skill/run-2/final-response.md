All six cases match exactly what `test/report.bats` asserts (status codes and stdout/JSON payloads), and `shellcheck`/`bash -n` are clean on both the script and test files.

One gap to flag: `bats-core` isn't installed in this sandbox (`make test` fails with "bats: No such file or directory"), and installing it wasn't something I did without asking, per the package-install rule in CLAUDE.md. I verified behavior by running the script directly with the exact inputs/assertions from `report.bats` instead of through the real runner — that's a substitute for, not equivalent to, the bats suite itself.

Files changed:
- `bin/report.sh` — added `--json` flag (position-independent), usage string now `[--json] FILE`, text output unchanged.
- `test/report.bats` — added JSON-mode, flag-order, and `--json`-without-file cases.

Before trusting this as fully verified, install `bats-core` (e.g. `apt-get install bats` or `npm install -g bats`) and run `make test` — want me to do that now?
