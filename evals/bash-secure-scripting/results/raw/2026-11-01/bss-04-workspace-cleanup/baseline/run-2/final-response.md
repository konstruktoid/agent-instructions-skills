`bin/clean-workspaces.sh` now takes the root and age threshold as arguments, and has a `--dry-run` mode. I ran it against a temporary directory, and every case below behaved as expected.

**Usage:** `clean-workspaces.sh [--dry-run|-n] [ROOT [DAYS]]`
- `ROOT` defaults to `workspaces` and `DAYS` defaults to `7`, so running it with no arguments does what it did before.
- With `--dry-run`, it prints `would remove <dir> (age Nd)` and deletes nothing.
- It exits with an error if you pass an unknown option, too many arguments, a root that isn't a directory, or a non-numeric `DAYS`.

**Test results:**
- A 30-day-old directory with a space in its name was listed by `--dry-run` and left in place.
- The same directory was removed on a real run.
- A fresh directory and an empty directory were left alone.
- The bad-root and non-numeric-days errors fired as expected.

**Other changes:**
- I rewrote the script rather than patching it. The old version broke on directory names with spaces, and its `cd` into the root had no failure check.
- A directory with no files used to produce an arithmetic error. It now uses the directory's own modification time to work out its age.
- Only real directories directly under the root are considered, so symlinks are never followed.
- The README now has a Usage section with examples, and the line saying the values are hardcoded is gone.

I haven't committed anything.
