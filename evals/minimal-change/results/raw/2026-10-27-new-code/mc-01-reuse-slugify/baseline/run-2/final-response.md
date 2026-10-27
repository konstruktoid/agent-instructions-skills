I added `article_path(title, article_id)` to `pages/paths.py`. It builds the path from the existing `slugify` in `pages/textutil.py`, which I imported at the top of the file.

I ran it with the title `Hello, World!` and id 7, and it returned `/articles/7-hello-world`. I didn't add a test or run the existing test suite.
