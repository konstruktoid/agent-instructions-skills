I added `save_settings(path, settings)` to `app/settings.py`. It writes the dict as JSON with `indent=2` and sorted keys, followed by a newline. I didn't write a test for it or run it against a file. `ruff format` and `ty` pass, and `ruff check` reports nothing for the new function.

I gave the new function type annotations and used `Path(path).open(...)`, which meant importing `Path`. `ruff check` still reports three errors in `load_settings`. I left them alone since it wasn't part of the request, and `ruff check` over the whole repo also flags the existing test files.
