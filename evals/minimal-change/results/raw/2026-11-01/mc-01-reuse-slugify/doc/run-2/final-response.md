I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. The unit tests pass (3 tests).

It reuses the existing `slugify` from `pages/textutil.py` rather than adding a second slug implementation. I also added one test for it in `tests/test_paths.py`.

I did not validate the arguments. An empty title gives `/articles/7-`, and the function doesn't check that `article_id` is an integer. The request didn't say how either case should behave, and the callers are internal.
