I don't have file-write tools available in this session (only Glob/Grep/Read/Skill), so I can't create the file directly. Here's the config loader to add as `src/ledger/config.py`:

```python
"""Load operator-supplied YAML configuration files."""

import argparse
import sys
from pathlib import Path

import yaml


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the --config path argument."""
    parser = argparse.ArgumentParser(description="Load a YAML config file.")
    parser.add_argument("--config", required=True, type=Path, help="Path to the YAML config file")
    return parser.parse_args(argv)


def load_config(path: Path) -> dict:
    """Read and parse a YAML config file, rejecting arbitrary object tags."""
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config file {path} must contain a YAML mapping at the top level")
    return data


def main(argv: list[str] | None = None) -> dict:
    args = parse_args(argv)
    return load_config(args.config)


if __name__ == "__main__":
    print(main(sys.argv[1:]))
```

Key security points:
- Uses `yaml.safe_load`, never `yaml.load`/`yaml.unsafe_load` — the default `Loader` can instantiate arbitrary Python objects from tags like `!!python/object`, which is a known RCE vector for untrusted or even semi-trusted YAML.
- Validates the parsed result is a mapping before returning it, so callers don't get surprised by a list/scalar/`None` and treat it as a dict downstream.
- The path itself comes from the operator's own CLI invocation (trusted input), so no additional path-traversal/allowlist checks are needed there — that's the boundary that matters for SSRF/traversal-style issues, not here.

You'll also need `pyyaml` declared as a dependency (e.g. in `pyproject.toml`). Want me to check what's missing so a Write-capable session can apply this, or would you like to add the file yourself and have me review it once it exists?
