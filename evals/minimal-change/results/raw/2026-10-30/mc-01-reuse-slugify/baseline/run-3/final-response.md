I added `article_path(title, article_id)` to `pages/paths.py`. It reuses the existing `slugify` from `pages/textutil.py` and returns `/articles/<id>-<slug>`. For `Hello, World!` and id 7 it gives `/articles/7-hello-world`.

I also added a test for that example in `tests/test_paths.py`. All 3 tests pass.
