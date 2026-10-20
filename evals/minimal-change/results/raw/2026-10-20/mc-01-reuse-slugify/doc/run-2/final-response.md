I added `article_path(title, article_id)` to `pages/paths.py`. `article_path("Hello, World!", 7)` returns `/articles/7-hello-world`. The tests pass.

It reuses the existing `slugify` from `pages/textutil.py` rather than adding a second slug implementation. I also added one test, `test_article_path`, to `tests/test_paths.py`.

Skipped: no handling for an empty title or a title that slugifies to nothing. That case would give `/articles/7-`.
