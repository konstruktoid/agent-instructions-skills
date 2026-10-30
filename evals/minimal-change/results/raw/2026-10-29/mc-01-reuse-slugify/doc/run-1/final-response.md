I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `article_path("Hello, World!", 7)` gives `/articles/7-hello-world`. The three tests pass.

It reuses the existing `slugify` from `pages/textutil.py` instead of a new slug routine. I also added one test for it in `tests/test_paths.py`.

Skipped: I didn't validate `article_id`. It is formatted as given, and an empty or all-symbol title gives a path ending in `<id>-`.
