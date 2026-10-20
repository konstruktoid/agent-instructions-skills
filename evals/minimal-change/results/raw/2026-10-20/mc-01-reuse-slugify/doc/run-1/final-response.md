I added `article_path(title, article_id)` to `pages/paths.py`. It reuses the existing `slugify` from `pages/textutil.py` instead of a new slug routine. I ran `article_path('Hello, World!', 7)` and got `/articles/7-hello-world`.

Skipped: I added no test, since the function is one f-string and `slugify` already has tests. I also did not run the existing test suite. A title that slugifies to an empty string gives `/articles/7-`.
