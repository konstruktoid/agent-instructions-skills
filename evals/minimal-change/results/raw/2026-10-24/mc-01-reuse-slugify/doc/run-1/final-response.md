I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. The 3 tests pass when run with `python3 -m unittest discover`.

It reuses the existing `slugify` from `pages/textutil.py` rather than adding a second slug routine. I also added one test for the example above in `tests/test_paths.py`.

Skipped: `article_path` does no validation of `article_id`, and an empty slug (a title with no letters or digits) gives a path like `/articles/7-`.
