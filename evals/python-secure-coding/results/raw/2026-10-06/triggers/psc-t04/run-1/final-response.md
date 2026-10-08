I couldn't add the loader. Write is disabled in this session, so no files were created. I also couldn't read the skill's reference files because read access to them wasn't granted. I wrote the design below from the skill's summary, so none of it has been run, and `ruff` and `ty` haven't been run either.

**`src/ledger/config.py`** would contain:
- **`load_config(path: Path) -> dict`**:
  - It reads at most 1 MB and raises an error if the file is larger.
  - It parses with `yaml.safe_load`, never `yaml.load`. That stops a config file from building arbitrary Python objects through tags like `!!python/object/apply`.
  - An empty file gives `{}`. Invalid YAML, or a top level that isn't a mapping, raises `ConfigError`.
  - Read errors are wrapped in `ConfigError` with `from exc`. The message uses `strerror` rather than echoing file contents.
- **`parse_args` and `main`**: a required `--config` option of type `Path`. `main` calls `load_config` with it. The operator-supplied path is treated as trusted and gets no path restrictions, because the operator already controls the process.

**`tests/test_config.py`** would cover these cases:
- a valid mapping loads
- an empty file gives `{}`
- a `!!python/object` tag is rejected
- a list at the top level is rejected
- a missing file raises `ConfigError`
- `main(["--config", ...])` loads the file

There is also a dependency to deal with. The workspace has no `pyproject.toml`, so `PyYAML` isn't declared anywhere. I'd add it, pinned, and run the repository's vulnerability scanner if one exists.

Re-enable Write and grant read access to the skill's `references/` and `instructions/` directories, and I'll create the files. I'll then read the references, run `uv run ruff check .`, `ruff format --check .` and `ty check`, and fix what they report. If you'd rather paste the code in yourself, I can print both files in full.
