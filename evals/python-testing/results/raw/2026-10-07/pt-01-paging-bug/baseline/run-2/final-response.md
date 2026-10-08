I fixed `page_slice` in `src/paging/slicing.py`. The cause was an `end = min(start + per_page, len(items) - 1)` line that capped the slice one item short. It now returns `items[start : start + per_page]`. Python slicing already clamps at the end of the list, so six letters two at a time give three full pages. A page past the end returns `[]` instead of raising.

I added three tests to `tests/test_slicing.py`:
- The last page of six letters at two per page is `["e", "f"]`.
- Concatenating every page reproduces the original list, so each item appears exactly once.
- A page past the end is `[]`.

Check results:
- **pytest:** 11 passed.
- **ruff format:** clean.
- **ruff check:** it flagged an import-ordering problem in `tests/test_slicing.py`, which I fixed with `--fix`. That was there before my change.
- **ty:** it passes with `ty check --project . --extra-search-path src src tests`. A plain `ty check` fails. It picks up a parent directory as the project root and can't resolve `paging`, and it also reports diagnostics from an unrelated `check_skills.py` outside this repo. I didn't change the project's ty configuration. Say so if you want that set up in `pyproject.toml`.

I left the untracked `__pycache__` directories alone. There's no `.gitignore`, so they will show up in `git status`.
