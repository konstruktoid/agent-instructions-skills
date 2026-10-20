I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. The three tests pass (`python3 -m unittest`).

It reuses the existing `slugify` from `pages/textutil.py` instead of a new slug routine. I also added one test for the `Hello, World!` example to `tests/test_paths.py`.

I didn't validate the title or id. A title that slugifies to an empty string gives `/articles/7-`.
