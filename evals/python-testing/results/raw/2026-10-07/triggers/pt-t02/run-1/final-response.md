I couldn't find `parse_manifest` anywhere in this checkout, so I haven't written any tests. I don't want to invent tests for a function I can't read.

- **Searched:** a case-insensitive search for `parse_manifest` and `ParseManifest` across the whole workspace returned nothing. The only Python sources are `src/ledger/balance.py` and `src/ledger/client.py`, and neither defines it.
- **Closest match:** `cmd/parser.go` has `Parse(line string) string`, which is documented as turning a manifest line into a record. It's Go and just returns its input, so it doesn't look like what you mean. The python-testing skill only covers Python and pytest, so it doesn't apply to it.
- **Existing tests:** the only test file is `tests/test_balance.py`. There's no `pyproject.toml`, `pytest.ini`, `tox.ini` or `conftest.py`. When I do write the tests, I'll follow the style in that file.

Because the function is new and public, the skill says it needs tests, including the failure paths for bad input.

Can you tell me which of these applies?
1. It's on another branch or uncommitted somewhere I can't see. The current branch is `eval-harness-delegation`. Please give me the branch or file path.
2. It lives in a different repository or directory.
3. You meant the Go `Parse` function. I can add a Go test in the repo's style instead, but that falls outside the pytest skill.
