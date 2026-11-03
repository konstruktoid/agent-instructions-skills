`bin/prune-artifacts.sh` now exits 1 with an error on stderr when the artifact directory doesn't exist. I checked it by running the script against a scratch directory. I didn't add a test file.

**Changes in `bin/prune-artifacts.sh`:**
- **Missing directory:** the script prints `prune-artifacts: artifact directory not found: <dir>` to stderr and returns 1. It no longer prints the "pruned …" line in that case.
- **`find` errors:** I also made a failing `find` (for example, a permission error) return 1 with its own message. You didn't ask for this, but the same silent-success problem would otherwise remain there.

**What I ran, all in a temporary directory:**

| Case | Result |
|---|---|
| Missing directory | Exit 1, empty stdout, message on stderr |
| Same missing directory, original script from `HEAD` | Exit 0 and "pruned …" printed, so the bug reproduces |
| Existing directory whose path contains a space | Exit 0; the 30-day-old file was deleted and the new file kept |
| Second run on the same directory | Exit 0, nothing further changed |

`shellcheck` and `bash -n` are clean. I didn't exercise the new `find`-failure branch.

The README says the repo has no automated tests and no test framework is set up, so I verified directly rather than adding a bats suite. If you want this behaviour locked in, a small `test/prune-artifacts.bats` covering the four cases above is the next step. `bats` is installed here.

I haven't committed anything.
