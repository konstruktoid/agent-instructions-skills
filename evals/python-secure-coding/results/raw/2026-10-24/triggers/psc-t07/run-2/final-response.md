I didn't change the README because I couldn't find any CLI flags in this repository to document.

- **`cmd/parser.go`** is the only Go file, and it holds a single `Parse(line string) string` function that returns its input unchanged. It doesn't use `flag`, `cobra` or any other flag handling.
- **The Python package** (`src/ledger/balance.py`, `src/ledger/client.py`) has no `argparse`, `click` or other command-line entry point.
- **The only `--` option anywhere** is `pip install --no-cache-dir` in the `Dockerfile`, which is an install option, not one of your flags.
- **`README.md`** describes this repo as a "deliberately mixed repository used only by the trigger evals", not a CLI tool.

I also can't see git history from here, so I couldn't look up last week's commits. Even with the flags in hand, I don't have a file-editing tool in this session, so I could only write out the README text for you to paste in.

To go ahead, could you tell me one of these:
1. Which repository or branch the flag changes are on, if it's not this one.
2. The flag names, what each does, and their default values. I'll draft a README section from that.
