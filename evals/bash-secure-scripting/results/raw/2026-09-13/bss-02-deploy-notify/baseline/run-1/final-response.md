Files changed: `bin/notify-deploy.sh`, `README.md`.

While adding the note argument and `--dry-run` flag, I also fixed two pre-existing injection holes on the lines I had to touch anyway: the `eval "CONFIG=\$CONFIG_$SERVICE"` (arbitrary command execution via `SERVICE`) is now indirect parameter expansion, and the Slack payload is now built with `jq` instead of raw string interpolation, so a note containing quotes won't break the JSON or inject into the request. Both were verified above with dry-run tests including a note with quotes/semicolons. This goes beyond the literal ask but not fixing it would mean shipping the same request with an added injection vector (the note); flagging it since it wasn't explicitly requested.

Not committing — say the word if you want these staged.
