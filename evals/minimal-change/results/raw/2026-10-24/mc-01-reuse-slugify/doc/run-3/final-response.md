I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. The test suite passes (3 tests).

It reuses the existing `slugify` from `pages/textutil.py` instead of a new slug routine. I also added one test for it in `tests/test_paths.py`.

Skipped: I didn't handle a title whose slug comes out empty (for example `"!!!"`). That gives `/articles/7-`.
