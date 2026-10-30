I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>` and reuses the existing `slugify` from `pages/textutil.py`. I ran it with `Hello, World!` and id 7, and it returned `/articles/7-hello-world`.

I did not add a test, because the function is a single f-string and `slugify` already has its own test. I did not run the existing test suite.
