I added `article_path(title, article_id)` to `pages/paths.py`. `article_path("Hello, World!", 7)` returns `/articles/7-hello-world`. It reuses the existing `slugify` from `pages/textutil.py` instead of building a second slug function. I also added one test in `tests/test_paths.py`, and the suite passes (3 tests).

Nothing was skipped. I did not validate `title` or `article_id`, since the request didn't ask for it and the function's callers are inside the repo.
