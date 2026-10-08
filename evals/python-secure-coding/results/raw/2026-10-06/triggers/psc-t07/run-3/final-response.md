I haven't changed the README, because I couldn't find any CLI flags to document.

- **The README:** `README.md` describes the repo as a sandbox for trigger evals and has no CLI or usage section.
- **The code:** a search of the workspace found no `argparse`, `click`, `typer` or `sys.argv` use. It also found no `--flag`-style options and no mention of "flag" or "CLI". The only `--` match was `--no-cache-dir` in the Dockerfile's `pip install`.
- **Git history:** I didn't run `git log` for last week's commits, so I can't rule out that the flags are in a commit not checked out here. The recent commits I can see (`python-security-verifier` measurements, trigger ancestry, the pv-04 control fix) don't mention CLI flags.

The flags may be on another branch or in a different repository, such as the parent eval harness, since the git status shows the workspace sits inside a larger untracked directory.

Can you tell me which branch, commit or path they're in? If you paste the flag names and what each does, I can write the section directly.
