I couldn't find any new CLI flags, so I haven't changed the README.

- **No flags in the code.** Nothing in the workspace defines a CLI (no `argparse`, `click`, `typer` or `sys.argv`). The only Python module that matched my search is `src/ledger/client.py`, and it's a retry client with no command-line interface.
- **README scope.** `README.md` only describes this repo as a mixed sandbox for trigger evals. It has no usage or options section where flags would go.
- **Git history not checked.** I only used the search tools, so I haven't looked at last week's commits. The recent ones on this branch are about eval measurements and delegation patterns, not CLI flags.

The flags may be on another branch or in a different repo. Which branch or commit added them, or which flags should I document? If you give me the flag names and what they do, I can add a section to the README.
