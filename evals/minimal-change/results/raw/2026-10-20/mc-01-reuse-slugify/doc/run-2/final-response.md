I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, and `article_path("Hello, World!", 7)` gives `/articles/7-hello-world`. I ran that one call by hand and did not run the test suite.

It reuses the existing `slugify` from `pages/textutil.py`, so there is no new slug logic. I added no test because the function only joins the id and the slug, and `slugify` already has its own test.

I did not check what `slugify` returns for an empty title or one with no ASCII letters.
