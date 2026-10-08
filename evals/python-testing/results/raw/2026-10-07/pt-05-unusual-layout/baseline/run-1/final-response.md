I added `running_balance(entries, account)` to `src/ledger/balance.py` and exported it from `ledger/__init__.py` next to `Entry` and `balance`. It returns the cumulative balance after each entry for that account, in order. It skips other accounts' entries and returns `[]` if the account has none.

I added two checks to `src/ledger/_tests/check_balance.py`, one for accumulation and ordering and one for an unknown account. The repo collects `check_*` files from that directory, so I put them there and not in the top-level `tests/`. `uv run pytest` passes with 4 checks, and `ruff check`, `ruff format --check` and `ty check src` are clean.

Plain `ty check` with no path reports 14 diagnostics, none from this repo's code. The first one I saw points at a line in a dependency's `version = entry.get("version")` code, and I didn't look at the rest.

The existing `balance` check for an unknown account goes through `_helpers.check_values`, which prints a mismatch and never fails. That check can't catch a regression, so I used plain `assert` in the new checks. I left the helper alone since its docstring says the tolerance is deliberate for now.

My first attempt ran one `cd` from the wrong directory and left the new checks duplicated. I removed the duplicates and re-ran everything above on the final state.
