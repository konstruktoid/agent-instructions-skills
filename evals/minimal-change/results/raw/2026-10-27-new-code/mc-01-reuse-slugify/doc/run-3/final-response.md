I added `article_path(title, article_id)` to `pages/paths.py`. `article_path("Hello, World!", 7)` returns `/articles/7-hello-world`. I also added a test for that example in `tests/test_paths.py`, and the suite passes.

It reuses the existing `slugify` from `pages/textutil.py` instead of writing a second slug routine.

Skipped: I didn't validate `article_id`, and a title that slugifies to an empty string gives a path like `/articles/7-`. I only ran the unit tests, not the site.
