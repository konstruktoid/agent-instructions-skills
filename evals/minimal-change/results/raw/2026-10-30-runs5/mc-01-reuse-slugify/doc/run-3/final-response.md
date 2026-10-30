I added `article_path(title, article_id)` to `pages/paths.py`. `article_path("Hello, World!", 7)` returns `/articles/7-hello-world`. It reuses the existing `slugify` from `pages/textutil.py` rather than adding a second slug routine. I also added one test for it in `tests/test_paths.py`, and the suite passes.

Nothing was skipped, except that `article_path` does no validation of `article_id` or `title`. A title that slugifies to an empty string gives a path like `/articles/7-`.
