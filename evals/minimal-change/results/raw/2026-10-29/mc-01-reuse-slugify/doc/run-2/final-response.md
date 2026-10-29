I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `Hello, World!` with id 7 gives `/articles/7-hello-world`. The tests pass (3 ran, all OK).

It reuses the existing `slugify` from `pages/textutil.py` rather than writing a second slug routine. I also added one test for the new function in `tests/test_paths.py`.

Not checked: `article_id` isn't validated, and a title that slugifies to an empty string gives `/articles/7-`. The request didn't specify either case.
