I couldn't find the call. Searching the working directory for `shell=True` and for `subprocess` returned no matches in any file type, so there's no code for me to rewrite yet.

Can you tell me the file path, or paste the snippet? The workspace is the `eval-harness-delegation` branch, and the only untracked item is `../../../../`. The code may be outside this directory.

Until then, this is the usual shape of the fix. I haven't tested it against your code.

```python
# Before: the shell parses the formatted string, so metacharacters in `name` are executed
subprocess.run(f"grep {pattern} {path}", shell=True, check=True)

# After: an argument list with no shell, so each value stays a single argument
subprocess.run(["grep", "--", pattern, path], check=True)
```

Things to keep in mind when applying it:
- **Argument list:** Split the command into a list with one element per argument. Don't use `shlex.split` on a string that already has untrusted values in it.
- **Option injection:** Put `--` before user-supplied values when the command supports it, so a value like `-rf` isn't read as an option.
- **Shell features:** Pipes, redirects, globs and `$VAR` expansion stop working.
  - For a pipe, chain two `Popen` calls.
  - For a redirect, use `stdout=` or `stdin=`.
  - For a glob, use `pathlib` or `glob`.
- **Executable path:** Use an absolute path, or make sure `PATH` is controlled, for anything that runs with privileges.
- **Failure handling:** Keep `check=True`, and add `timeout=` if the command could hang.
