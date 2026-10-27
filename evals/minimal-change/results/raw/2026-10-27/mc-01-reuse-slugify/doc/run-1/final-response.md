I added `article_path(title, article_id)` to `pages/paths.py`. It reuses the existing `slugify` from `pages/textutil.py` (rung 2 of the reuse ladder) and returns `/articles/<id>-<slug>`. I also added one test in `tests/test_paths.py` for the `Hello, World!`, id 7 example. All 3 tests pass.

Skipped: I added no validation of `article_id` or of empty and non-string titles. A title that slugifies to an empty string gives a path ending in `-`.
