Works correctly: dry-run skips ssh/curl, and the note's embedded quotes are escaped rather than breaking the JSON payload.

Files changed: `bin/notify-deploy.sh`, `README.md`.

One thing worth flagging since I touched this file: `SERVICE` still flows unquoted into `eval` and the `ssh` remote command (lines predate this change) — that's a command-injection risk if `SERVICE`/`VERSION` ever come from anything other than a trusted operator typing them at a shell. I didn't fix it since it's out of scope for what you asked, but it's a pre-existing exposure, not one I introduced.
