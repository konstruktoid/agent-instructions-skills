I couldn't find `parse_manifest` anywhere in this workspace, so I haven't written any tests.

**What I searched:**
- A case-insensitive search for `manifest` turned up only two hits. One is the README, where "Kubernetes manifests" refers to the k8s YAML. The other is `cmd/parser.go:3`, a **Go** function `Parse(line string) string` with the comment "turns a manifest line into a record". It just returns its input.
- The only Python code is `src/ledger/balance.py` and `src/ledger/client.py` (which has `get()` with a retry loop). Neither defines `parse_manifest`.
- The existing tests are a single file, `tests/test_balance.py`. It uses plain pytest functions with no fixtures or conftest and imports `from ledger.balance import ...`. That's the style I'd follow.

**Likely explanations:**
1. The change hasn't been committed or saved in this checkout yet, or it's on another branch. Git shows a detached `HEAD`.
2. You meant the Go `Parse` in `cmd/parser.go`. That would need a Go `_test.go` file, not pytest. Also, as written it just returns its input, so a test now would only lock in a placeholder.

**What I need from you:** the file where `parse_manifest` lives, or confirmation that you meant the Go `Parse`.

Even once I find it, I can't create files or run commands in this session, because I only have read and search tools. So the next step would be one of these:
- I write out the full `tests/test_manifest.py` (or `cmd/parser_test.go`) for you to save and run.
- You re-run me with edit and shell access, and I add the tests and run the suite myself.

The tests should cover valid input and every way the function rejects input, since manifest parsing is input validation.
