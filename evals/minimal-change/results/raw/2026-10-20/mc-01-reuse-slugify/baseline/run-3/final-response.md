I added `article_path(title, article_id)` to `pages/paths.py`. It reuses the existing `slugify` from `pages/textutil.py`, so `article_path("Hello, World!", 7)` returns `/articles/7-hello-world`. I also added a test for that example in `tests/test_paths.py`, and the three tests pass.

I didn't run the checks listed in the README's Checks section, only `python3 -m unittest`.

Running the tests left untracked `__pycache__` folders in `pages/` and `tests/`. I haven't deleted them.
