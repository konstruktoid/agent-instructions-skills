I added `article_path(title, article_id)` to `pages/paths.py`. It builds the path from the existing `slugify` in `pages/textutil.py`, so I imported that at the top of the file.

I ran `article_path("Hello, World!", 7)` and it returned `/articles/7-hello-world`. I didn't add a test or run the existing test suite.
