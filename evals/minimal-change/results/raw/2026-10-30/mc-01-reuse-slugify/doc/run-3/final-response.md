I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. It reuses the existing `slugify` from `pages/textutil.py` instead of a second slug implementation. I also added one test to `tests/test_paths.py` for that example. The suite passes (3 tests).

Skipped: nothing. I didn't validate `title` or `article_id`, since callers are internal code, not a trust boundary.
