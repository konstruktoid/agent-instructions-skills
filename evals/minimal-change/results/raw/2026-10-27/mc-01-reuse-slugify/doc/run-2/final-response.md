I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. The unit tests pass (3 tests, including the new one).

It reuses the existing `slugify` from `pages/textutil.py` rather than writing a second slug routine. I also added one test for `article_path` in `tests/test_paths.py`.

I did not validate `article_id`, because you didn't ask for it and the function only formats a path. A title that slugifies to an empty string would give `/articles/7-`.
