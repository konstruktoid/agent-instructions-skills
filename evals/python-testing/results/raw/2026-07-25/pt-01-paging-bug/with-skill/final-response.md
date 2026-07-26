Everything looks clean. Summary:

**Bug fix** (`src/paging/slicing.py`): `end` was computed as `min(start + per_page, len(items) - 1)`, which capped the slice end one short of the sequence length — always dropping the last item, and on smaller sequences making it unreachable on any page. Fixed to `end = start + per_page`; Python's slicing already clamps to the sequence length and returns `[]` when `start` is past the end, so no extra bounds logic is needed.

**Tests** (`tests/test_slicing.py`): added `test_page_slice_includes_the_last_item_on_the_final_page` (confirmed it fails on the unfixed code — got `['e']` instead of `['e', 'f']`) and `test_page_slice_past_the_end_returns_an_empty_list`. Ruff also reordered the import block.

**Checks**: found the `ty` type check was pre-existing broken (couldn't resolve the `paging` import, independent of this change — verified via `git stash`) because it lacked the module-resolution root that `pytest` already had via `pythonpath = ["src"]`. Added the equivalent `[tool.ty.environment] root = ["src"]` to `pyproject.toml`. `pytest`, `ruff check`, `ruff format --check`, and `ty check` all pass now.
