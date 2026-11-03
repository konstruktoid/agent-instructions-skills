I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. The unit tests pass (3 run).

It reuses the existing `slugify` from `pages/textutil.py` instead of a new slug routine. I also added one test for it in `tests/test_paths.py`.

Skipped: I didn't validate `title` or `article_id`, since the callers are internal. An empty or symbol-only title gives `/articles/7-`.
