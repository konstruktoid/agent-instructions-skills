I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>` and builds the slug with the existing `slugify` from `pages/textutil.py`, which is now imported at the top of the file.

I checked it by running `article_path('Hello, World!', 7)`, which returned `/articles/7-hello-world`. I didn't add a test or run the existing test suite.
