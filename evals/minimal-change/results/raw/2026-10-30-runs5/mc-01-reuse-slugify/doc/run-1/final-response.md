I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. The test suite passes.

It reuses the existing `slugify` in `pages/textutil.py` rather than adding a second slug implementation. I also added one test in `tests/test_paths.py` for your example.

Skipped: `article_id` isn't validated, since the request didn't ask for it and callers inside the repo pass it. A title that slugifies to an empty string gives a path like `/articles/7-`.
