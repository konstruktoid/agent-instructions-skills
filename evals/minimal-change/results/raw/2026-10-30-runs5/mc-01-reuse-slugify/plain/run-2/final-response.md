I added `article_path(title, article_id)` to `pages/paths.py`. It builds the path with the existing `slugify` from `pages/textutil.py`, so I imported that rather than writing new slug logic.

I ran it once with the example from your request. `article_path('Hello, World!', 7)` returns `/articles/7-hello-world`. I didn't run any other tests.
