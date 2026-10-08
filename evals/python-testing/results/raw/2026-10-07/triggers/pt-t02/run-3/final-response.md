I can't find `parse_manifest` anywhere in this workspace, so I haven't written any tests.

- A search of every file for `parse_manifest` returned nothing. That includes `src/ledger/balance.py` and `src/ledger/client.py`.
- The only Python tests are in `tests/test_balance.py`. They use plain top-level `test_*` functions with a docstring and a bare `assert`. There is no `conftest.py` and no pytest config.
- `cmd/parser.go` is Go, so pytest doesn't apply to it.

The function may be on another branch, or uncommitted somewhere I can't see. I'm on `eval-harness-delegation`. It may also have a different name or live in a different repo.

Where is `parse_manifest` defined? A file path or branch name is enough. Once I can read it, I'll write the tests in the existing style, in `tests/test_<module>.py`. They'll cover the normal path and the rejection paths for malformed input. Then I'll run the suite.
