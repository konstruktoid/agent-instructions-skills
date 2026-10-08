I couldn't find any CLI flags to document, so I haven't changed the README.

- **No flag-parsing code:** There's no `argparse`, `click` or `typer` anywhere in the repo. The only Python files are `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`.
- **No flags in the scripts:** The only `--flag` in the repo is `--no-cache-dir` in the `Dockerfile`, which is a `pip` option, not one of yours.
- **README content:** It only describes this repo as a trigger-eval sandbox, and it has no usage or CLI section.
- **Recent commits:** The latest ones are about eval-harness work (measurements, trigger ancestry, delegation reports). None of them mention new flags.

The flags may be on another branch, in a different repo (for example the parent eval harness that contains this workspace), or not committed yet.

Which branch, repo or commit range are they in? If you paste the flag names and what each does, I can write the README section from that.
