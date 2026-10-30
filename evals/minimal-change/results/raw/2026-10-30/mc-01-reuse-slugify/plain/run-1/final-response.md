I added `article_path(title, article_id)` to `pages/paths.py`. It returns `/articles/<id>-<slug>`, building the slug with the existing `slugify` from `pages/textutil.py`. I haven't run it, so `/articles/7-hello-world` for `Hello, World!` and id 7 is untested.

I added `from pages.textutil import slugify` at the top of the file. I assumed `pages` is importable as a package, so that import path is unchecked too.
