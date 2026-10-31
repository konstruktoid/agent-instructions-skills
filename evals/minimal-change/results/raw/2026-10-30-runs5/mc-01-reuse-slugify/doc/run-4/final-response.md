I added `article_path(title, article_id)` to `pages/paths.py`. It reuses the existing `slugify` from `pages/textutil.py` (reuse-ladder rung 2). `article_path("Hello, World!", 7)` returns `/articles/7-hello-world`.

Skipped: I added no test, since the function is a single f-string around the already-tested `slugify`. I didn't run the existing test suite. I also didn't validate `article_id`, because the function is only called internally.
