I couldn't find a `parse_manifest` function in this workspace, so I haven't written any tests.

**What I checked:**
- **No `parse_manifest` anywhere.** Searching the whole repo for the name found nothing.
- **The Python package has two modules,** `src/ledger/balance.py` and `src/ledger/client.py`. Neither one defines `parse_manifest` or anything about manifests. `client.py` has only `get()`, a retrying fetch.
- **The closest match is in Go.** `cmd/parser.go:3` has `Parse(line string)`, whose comment says it "turns a manifest line into a record." The Python testing approach I'd use doesn't apply to it, and right now it just returns its input.
- **Test conventions, for when the function turns up:** tests live in `tests/` as `test_<module>.py`. They're plain pytest functions with a docstring each, they import from `ledger.<module>`, and there's no `conftest.py`, fixtures or mocking. I found no `pyproject.toml` or `pytest.ini`, so the suite would run with plain `pytest`.

**Possible reasons:**
1. The change hasn't been saved or committed to this working tree yet, or it's on another branch. This checkout is a detached HEAD.
2. The function has a different name, or it lives outside this repo.
3. You meant the Go `Parse` in `cmd/parser.go`. That would need a Go `_test.go` file, not pytest.

Can you point me to the file or branch with `parse_manifest`, or confirm you meant the Go function?

Also, I can only read and search files in this session, not create them. Once I know where the function is, I can give you the full test file to add (normal input, edge cases and invalid input), or write it myself if file-editing access is turned on.
