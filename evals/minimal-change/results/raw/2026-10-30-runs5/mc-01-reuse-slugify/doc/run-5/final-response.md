I added `article_path(title, article_id)` to `pages/paths.py`. `article_path("Hello, World!", 7)` returns `/articles/7-hello-world`. The unit tests pass.

It reuses the existing `slugify` from `pages/textutil.py` rather than writing a new slug routine. I also added one test for it in `tests/test_paths.py`.

Nothing was skipped. `article_path` doesn't validate `article_id`, because it's an internal helper and not a trust boundary.
