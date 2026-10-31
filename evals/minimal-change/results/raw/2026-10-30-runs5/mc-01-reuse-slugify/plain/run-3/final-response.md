I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>` and reuses the existing `slugify` from `pages/textutil.py`, so I added `from pages.textutil import slugify` at the top of the file.

I ran it with `Hello, World!` and id 7, and it returned `/articles/7-hello-world`. I didn't run any other tests.
