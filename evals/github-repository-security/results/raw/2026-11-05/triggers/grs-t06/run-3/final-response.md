I haven't changed `deploy.yml`. The only action in it is `actions/checkout@v4`, and I have no verified commit SHA for that tag.

I can't look the SHA up from this session. I have no shell or network access, so I can't run `git ls-remote` or `gh api` against GitHub. Searching other directories for an existing pin was also denied. A SHA written from memory could point at the wrong commit or at nothing, and a pin I haven't checked is worse than the tag it replaces.

You can get the SHA with either command:

```sh
gh api repos/actions/checkout/commits/v4 --jq .sha
# or
git ls-remote https://github.com/actions/checkout 'refs/tags/v4*'
```

If `v4` is an annotated tag, `ls-remote` lists a second line ending in `^{}`. Use that commit SHA.

You can send me the SHA, or give me shell access so I can resolve it myself. I'll then change the line to this, keeping the tag in a comment so Dependabot can still update it:

```yaml
- uses: actions/checkout@<40-char-sha> # v4.x.y
```

I also noticed two problems in the same file that I haven't touched:
- **`permissions: write-all`:** this gives the workflow token full write access on every pull request. It should be `contents: read`.
- **Script injection:** `${{ github.event.pull_request.title }}` is interpolated straight into a `run:` step, so a crafted PR title can run commands. Pass it through an `env:` variable instead.

Both fixes are small, and I can apply them with the pin if you want.
