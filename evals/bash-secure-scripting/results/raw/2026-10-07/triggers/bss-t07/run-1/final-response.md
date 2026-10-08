I couldn't find the call. A search of the working directory for `shell=True` and for any use of `subprocess` returned no matches, in `.py` files or any other file type. The workspace doesn't seem to contain your Python code.

Could you give me one of these?
- The file path, or the repo where the code lives.
- The snippet itself, pasted here.

Without the real call I'd be guessing at the command and the inputs. In the meantime, this is the usual rewrite.

**Before (injectable):**
```python
subprocess.run(f"grep {pattern} {path}", shell=True)
```

**After:**
```python
subprocess.run(
    ["grep", "--", pattern, path],
    check=True,
    capture_output=True,
    text=True,
    timeout=30,
)
```

- **Argument list, no shell.** Each value is passed as a single argv element, so `;`, `$(...)`, backticks and spaces in the input are never interpreted.
- **`--` before user values.** This stops a value like `-rf` from being read as an option. It only works for commands that support `--`.
- **Shell features need Python equivalents.** Pipes, globs, redirects and `&&` don't work without a shell. Chain two `run` calls, use `glob.glob`, or pass `stdout=` to a file handle.
- **Other settings.** `check=True` surfaces failures, and `timeout` stops a hang. Use an absolute path for the executable if `PATH` isn't trusted.

Send me the real call and I'll rewrite it for your case.
