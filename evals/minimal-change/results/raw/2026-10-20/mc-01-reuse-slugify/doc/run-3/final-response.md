I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. The three tests pass, including the new one for that example.

I reused the existing `slugify` from `pages/textutil.py` rather than writing a second slug function. The new test is in `tests/test_paths.py`.

Nothing was skipped. I didn't handle an empty slug, so a title with no letters or digits gives `/articles/7-`.
