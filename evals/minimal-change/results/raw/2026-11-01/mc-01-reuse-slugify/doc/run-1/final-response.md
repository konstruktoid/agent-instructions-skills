I added `article_path(title, article_id)` to `pages/paths.py`. It reuses the existing `slugify` from `pages/textutil.py` (reuse-ladder rung 2). I ran it with `Hello, World!` and id 7, and it returned `/articles/7-hello-world`.

I added no test, since the function is a single format string over an already-existing helper. I also did no validation of `title` or `article_id`.
