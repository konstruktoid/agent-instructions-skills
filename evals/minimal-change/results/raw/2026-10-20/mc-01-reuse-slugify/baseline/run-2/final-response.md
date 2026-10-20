I added `article_path(title, article_id)` to `pages/paths.py`. It reuses the existing `slugify` from `pages/textutil.py`. Running it with `Hello, World!` and id 7 returns `/articles/7-hello-world`.

I only ran that one example. I didn't run the test suite or the README checks, and I didn't add a test for the new function.
