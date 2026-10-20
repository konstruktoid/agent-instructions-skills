I added `article_path(title, article_id)` to `pages/paths.py`. It reuses the existing `slugify` from `pages/textutil.py` rather than writing a second slug routine. A quick run gave `/articles/7-hello-world` for `Hello, World!` and id 7.

Skipped: I added no test, since the function is one f-string and `slugify` already has its own test. I didn't run the existing test suite.
