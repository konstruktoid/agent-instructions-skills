I added `article_path(title, article_id)` to `pages/paths.py`. It reuses the existing `slugify` from `pages/textutil.py`. A quick run with `Hello, World!` and id 7 returned `/articles/7-hello-world`.

I didn't run the unit tests or the README checks. I also didn't add a test for the new function.
