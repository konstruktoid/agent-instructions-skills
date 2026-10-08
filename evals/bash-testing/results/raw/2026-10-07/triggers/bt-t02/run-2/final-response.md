The repository has no convention for shell tests yet, so I'd start one. Put them in the existing `tests/` directory and name them after the script they cover.

**What exists today**
- There is one shell script, `scripts/backup.sh`.
- There are no `.bats` files, no `*_test.sh` or `test_*.sh` files, and no `Makefile` or `justfile`.
- `tests/` holds only `tests/test_balance.py`, a pytest test for the Python ledger helper.
- Neither CI file runs tests. `.github/workflows/deploy.yml` has no test step. `.gitlab-ci.yml` declares a `test` stage but defines no job in it.

**Recommendation**
- **Location:** `tests/`, the same directory the Python test uses. Don't add a second top-level `test/` directory next to it. If you'd rather keep the two languages apart, `tests/shell/` is a reasonable alternative.
- **Name:** `tests/backup.bats` for `scripts/backup.sh`. Use one test file per script, named after the script. This mirrors the existing `test_<module>.py` pattern.
- **Framework:** `bats-core`. It's the common choice for Bash, and nothing in the repo conflicts with it. Don't use the pytest suite. It tests Python, and `tests/test_balance.py` doesn't invoke any scripts.

**Things to settle when you add the first one**
- **Entry point:** nothing runs tests in CI, so you'd want a single command such as `bats tests/`. Adding it to `.gitlab-ci.yml`'s empty `test` stage would be the natural place. I haven't changed anything.
- **Testable script:** if `scripts/backup.sh` runs its logic at the top level, move it into functions. Keep the entry point as `main "$@"`, guarded so tests can source the file.
- **Skill snippet:** the guard example in the bash-testing skill, `[[ ${BASH_SOURCE[0]} == "Where" ]]`, looks corrupted. The usual form compares against `"${0}"`, so don't copy it verbatim.
- **Test content:** use a temporary directory for each test and stub external commands through `PATH`. Cover exit codes, bad arguments, and cleanup after a failed run.

I can scaffold `tests/backup.bats` for `scripts/backup.sh` if you want.
