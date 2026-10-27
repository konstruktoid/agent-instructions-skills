I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. The tests pass.

It builds the slug with the existing `slugify` in `pages/textutil.py` instead of a second implementation. I also added one test for the example case to `tests/test_paths.py`.

Skipped: nothing is validated. An empty title would give `/articles/7-`, and I didn't handle that because the request didn't ask for it.
