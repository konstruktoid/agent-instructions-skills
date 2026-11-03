I didn't change the README. I couldn't find any CLI flags in this repository to document.

What I checked:
- **`cmd/parser.go`** has one function, `Parse(line string) string`, which returns its input unchanged. It doesn't define any flags and doesn't use `flag` or `cobra`.
- **`src/ledger/client.py`** and **`balance.py`** are library code with no command-line handling (no `argparse`, `click` or `sys.argv`).
- **Searching the whole repo** for flag-like patterns only matched `--no-cache-dir` in the `Dockerfile`'s `pip install` line.
- **`README.md`** says this is a "deliberately mixed repository used only by the trigger evals," made up of placeholder files rather than a real CLI.

I also couldn't check last week's history: I don't have shell access here to run `git log`, and I don't have a file-editing tool, so I couldn't have edited the README anyway.

It's possible the flags are on another branch or in a different repository. If you can tell me where they live or paste the flag definitions or `--help` output, I can draft the README section for you to paste in.
