I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `article_path("Hello, World!", 7)` gives `/articles/7-hello-world`. The tests pass.

It reuses the existing `slugify` from `pages/textutil.py` instead of writing a second slug routine. I also added one test for it in `tests/test_paths.py`.

Skipped: `article_path` doesn't validate its arguments, and a title that slugifies to an empty string gives a path like `/articles/7-`.
