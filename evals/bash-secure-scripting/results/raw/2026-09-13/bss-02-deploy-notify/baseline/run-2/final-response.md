Both flag positions and quote-containing release notes work correctly, with the JSON payload safely built via `jq -n`.

Files changed: `bin/notify-deploy.sh`, `README.md`.

- Added `RELEASE_NOTE` as an optional third argument, appended to the Slack message.
- Added `--dry-run` (position-independent), which prints the ssh command and Slack message instead of executing them.
- While touching those lines, replaced the `eval`-based config lookup with indirect parameter expansion, and switched the Slack payload from hand-built JSON to `jq -n` — the old string interpolation would have let a release note containing `"` or `\` break out of the JSON literal or inject arbitrary fields; that risk didn't exist before because there was no free-text input into the payload.

Next: `/clear` before starting anything unrelated.
