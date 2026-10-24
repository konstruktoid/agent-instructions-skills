I couldn't find that call in this repository, so I haven't changed anything. Searches for `shell=True`, `subprocess`, `os.system` and `os.popen` found nothing. The only Python files are `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`, and none of them run a process.

If you paste the call or tell me which file it's in, I'll rewrite it. The fix usually looks like this:

**Before (vulnerable to shell injection):**
```python
subprocess.run(f"tar -czf {archive} {src_dir}", shell=True)
```

**After:**
```python
subprocess.run(
    ["tar", "-czf", archive, "--", src_dir],
    check=True,
)
```

What changes:
- **Pass a list of arguments instead of a string, and drop `shell=True`.** No shell reads the command, so characters like `;`, `$()`, backticks, `|` and spaces in `archive` or `src_dir` are treated as plain text, not commands.
- **Add `--` before user-supplied paths** if the command accepts it. Without it, a value starting with `-` would be read as an option.
- **Add `check=True`** so a failing command raises `CalledProcessError` instead of being silently ignored.
- **Use a full path to the program (e.g. `/usr/bin/tar`)** if the program is found through `PATH` and the environment might not be trusted.
- **Do pipes and redirects in Python.** For `cmd > out.txt`, pass `stdout=open(...)`. For `a | b`, chain two `Popen` calls or use `input=`/`capture_output=True`. Don't go back to `shell=True` for these.
- **If you really need shell features**, quote every value with `shlex.quote()`. It's a weaker fallback than the list form.
