I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, so `article_path("Hello, World!", 7)` gives `/articles/7-hello-world`. The full test suite passes.

I reused the existing `slugify` from `pages/textutil.py` instead of writing a new slug routine. I also added one test for the new function in `tests/test_paths.py`.

Skipped: `article_path` does no validation of `article_id`. It assumes callers pass a trusted id, and I didn't check what happens for an empty title.
