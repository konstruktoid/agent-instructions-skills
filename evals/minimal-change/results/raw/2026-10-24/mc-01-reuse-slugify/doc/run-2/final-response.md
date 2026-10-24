I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `article_path("Hello, World!", 7)` gives `/articles/7-hello-world`. All 3 tests pass.

It reuses the existing `slugify` from `pages/textutil.py` rather than a new slug routine. I also added one test for the example case to `tests/test_paths.py`.

Skipped: I didn't handle a title that slugifies to an empty string, such as `"!!!"`. That would give `/articles/7-`. I also didn't validate `article_id`.
