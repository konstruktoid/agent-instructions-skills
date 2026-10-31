I added `article_path(title, article_id)` to `pages/paths.py`. It builds the path with the existing `slugify` from `pages/textutil.py`. I ran `article_path("Hello, World!", 7)` and it returned `/articles/7-hello-world`. I didn't run any other tests.

The change also adds `from pages.textutil import slugify` at the top of the file.
