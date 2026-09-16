Changes: `.github/workflows/triage.yml` (new) and `README.md` (updated). YAML validated with `python3 -c "import yaml..."`.

Design notes worth flagging:
- Uses `pull_request_target` (not `pull_request`) because forked PRs get a read-only `GITHUB_TOKEN` under `pull_request` — no amount of `permissions:` config fixes that.
- No checkout step anywhere, so fork-controlled code is never executed with the elevated token — the classic `pull_request_target` risk doesn't apply here.
- All three fields you asked for (username, title, `needs-triage` label) come straight off `context.payload.pull_request`, not shell-interpolated, so a hostile PR title can't inject commands.
- Label creation is defensive: the add-labels endpoint 404s if `needs-triage` doesn't exist yet (unlike issue-creation, it doesn't auto-create), so I create it first and ignore the 422 if it's already there.

Not verified end-to-end against a live GitHub repo/fork PR — no such environment here. Recommend a quick real-world smoke test (open a PR from a fork against this repo) before relying on it.
