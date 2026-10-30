I added `article_path(title, article_id)` to `pages/paths.py`. It reuses the existing `slugify` from `pages/textutil.py`. Running `article_path('Hello, World!', 7)` returns `/articles/7-hello-world`.

I didn't add a test, because the function is a single f-string and `slugify` already has one. I also didn't run the existing test suite.
