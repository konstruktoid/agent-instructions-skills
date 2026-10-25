I extended `bin/archive-logs.sh` with multiple services, `--keep-days N` and a summary line, and updated the README. I ran it once against the sample logs and it worked. I haven't tested any other `--keep-days` values or option forms.

- **Multiple services:** you can now run `bin/archive-logs.sh api web`. The script checks every name before archiving anything. A bad or unknown service aborts the run with nothing written. A service named twice is archived once.
- **`--keep-days N`:** after all the new archives are written, it deletes `*-YYYYMMDD.tar.gz` files in `archives/` older than N days, going by modification time. It prunes every service's archives in that directory, not only the ones named in the run. The README says so. Without the flag, nothing is pruned.
- **Summary line:** on success it prints one line, for example `archived 2 service(s): api web; pruned 1 archive(s) older than 30 days`.
- **Other changes:**
  - **Safety:** the script now stops on any error, and service names are validated, so something like `../x` is rejected.
  - **Temp files:** it stages tarballs in a `mktemp` directory inside `archives/` and cleans up on exit. The old version used a predictable `/tmp` path.
  - **Working directory:** paths are still relative, so it must run from the repo root.
- **What I ran:** with a fake 40-day-old archive in place, `--keep-days 30 api web api` produced the line above and removed only the old file. `../x` exited with code 2 and `nope` exited with code 1. I deleted my test archives afterwards.

I did not commit anything.
