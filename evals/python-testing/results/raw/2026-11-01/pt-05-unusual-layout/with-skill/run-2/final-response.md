I added `running_balance(entries, account)` to `src/ledger/balance.py` and exported it from `ledger/__init__.py` next to `Entry` and `balance`. The repo's checks pass for the package: `uv run pytest` gives 5 passed, and `ruff check`, `ruff format --check` and `ty check src` are clean.

I ran `ty check src` rather than a bare `ty check`. The bare form walked up into the parent repository and reported 21 errors in files that aren't part of this repo, such as `run_eval.py` and `scripts/check_*.py`. I didn't touch those.

I added three checks to `src/ledger/_tests/check_balance.py`, the layout the README describes. I didn't put anything in the old top-level `tests/`, which isn't collected. They cover:
- a single account's cumulative totals (`[100, 70]`);
- interleaved entries for other accounts being ignored;
- an unknown account returning `[]`.

I didn't confirm that these checks fail without the new function. Since the function didn't exist before, they would fail on the import.

In `_tests/_helpers.py`, `check_values` catches the `AssertionError` and only prints a mismatch. The existing check that uses it (`balance` of an unknown account is zero) can therefore never fail. I used plain `assert` in the new checks and left the helper alone, since its comment says the tolerance is deliberate. You may want to tighten it.
