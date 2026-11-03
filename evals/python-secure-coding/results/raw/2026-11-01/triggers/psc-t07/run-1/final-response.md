I didn't change the README. I couldn't find any CLI flags in this repository to document.

- **No flag definitions:** I searched the whole workspace for `argparse`, `add_argument`, `click`, Go's `flag.` and `--option` patterns. The only match is `pip install --no-cache-dir` in the `Dockerfile`, and that isn't a flag of your tool.
- **The likely places have none:** `cmd/parser.go` has a single `Parse(line string) string` function that returns its input unchanged. `src/ledger/` has `balance.py` and `client.py`, and neither defines a command-line interface.
- **The README calls the repo a sandbox:** `README.md` says it's a "deliberately mixed repository used only by the trigger evals" with placeholder files. It doesn't describe a CLI.

I don't have shell access here, so I couldn't check git history for last week's changes. The flags may be on another branch, in a commit that isn't checked out, or in a different repository.

To go ahead, I need one of these:
1. The branch or repo where the flags were added, or
2. A list of the flags (name, argument, default, what each does), and I'll write the README section from that.
