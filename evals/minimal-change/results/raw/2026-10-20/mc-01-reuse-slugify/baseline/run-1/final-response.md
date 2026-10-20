I added `article_path(title, article_id)` to `pages/paths.py`. It builds the path with the existing `slugify` from `pages/textutil.py`, so `article_path("Hello, World!", 7)` returns `/articles/7-hello-world`.

I also added a test for that example in `tests/test_paths.py`. The full suite passes (3 tests, run with `python3 -m unittest`). I didn't run the checks listed in the README's Checks section.
