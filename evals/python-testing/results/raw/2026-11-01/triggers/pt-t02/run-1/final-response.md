I couldn't find a function named `parse_manifest` anywhere in this workspace, so I haven't written any tests yet.

What I searched:
- **`def parse_manifest`** appears nowhere in the repository.
- **The Python code** is only `src/ledger/balance.py` and `src/ledger/client.py` (which has `get`, a retrying transport call). Neither mentions a manifest.
- **The only manifest-related code** is in Go: `cmd/parser.go:4` has `func Parse(line string) string`, described as "turns a manifest line into a record". Right now it just returns its input unchanged. That's Go, so pytest wouldn't apply to it.
- **The existing tests** are one file, `tests/test_balance.py`: plain pytest functions named `test_<thing>_<behavior>` with one-line docstrings, a direct `from ledger.balance import ...`, no fixtures and no `conftest.py`. There's no `pyproject.toml` or `pytest.ini`.

Also, I only have read and search tools in this session, so I couldn't create a test file or run the suite even with the function in place.

To go further, I need one of these:
1. **The `parse_manifest` change itself.** It may be on another branch or not committed yet. Once it's here, I'll write `tests/test_manifest.py` in the same style as `test_balance.py`. It would cover a valid manifest and an empty one, plus the error cases (malformed input, missing required fields), since it's a public parser.
2. **If you meant the Go `Parse` in `cmd/parser.go`,** the tests should be Go tests in `cmd/parser_test.go`, not pytest.

Either way, I'll need write and shell access to add the tests and run them.
