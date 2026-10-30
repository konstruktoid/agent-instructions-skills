I added `article_path(title, article_id)` to `pages/paths.py`. It builds the path with the existing `slugify` from `pages/textutil.py`, so `article_path("Hello, World!", 7)` returns `/articles/7-hello-world`.

I ran that example and got the expected output. I didn't add a test, and I didn't run the existing test suite.
