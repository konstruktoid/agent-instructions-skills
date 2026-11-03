I haven't changed the README. I couldn't find any CLI flags in this repository to document.

- **No flag definitions:** I searched for `argparse`, `add_argument`, `click`, Go's `flag.` package and `--option` patterns. The only match was `pip install --no-cache-dir` in the `Dockerfile`, which isn't a CLI of this project.
- **No CLI entry point:** `cmd/parser.go` holds a single `Parse(line string) string` function with no flag handling. The Python package (`src/ledger/balance.py`, `client.py`) doesn't define a command-line interface either.
- **The README says this is a test repo:** it describes the project as a "probe-sandbox", a deliberately mixed repository used only by trigger evals.

The flags may be on another branch, in a commit that isn't checked out here, or in a different repository. If you tell me where they are, or give me the flag names and what they do, I can write the README section. I can't edit files in this session (I only have read and search tools), so I'd give you the Markdown to paste in.
