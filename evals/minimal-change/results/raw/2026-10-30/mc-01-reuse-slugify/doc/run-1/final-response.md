I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. The full test suite passes (3 tests).

I reused the existing `slugify` from `pages/textutil.py` for the slug. I also added `test_article_path` to `tests/test_paths.py`, which checks the example above.

Nothing was skipped. `article_path` doesn't validate `article_id`, because it's only called from inside the repo.
