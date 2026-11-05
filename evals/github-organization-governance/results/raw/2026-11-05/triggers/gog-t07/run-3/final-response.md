I couldn't make the change. The Edit tool is disabled in this session, and I have no other way to modify files here.

In `.github/workflows/deploy.yml`, replace line 7:

```yaml
permissions: write-all
```

with:

```yaml
permissions:
  contents: read
```

The job only runs `actions/checkout` and an `echo`, so read access to contents is enough. `write-all` gives the `GITHUB_TOKEN` write access to everything. That's a bad combination with a `pull_request` trigger.

I didn't change this, but line 14 has a script injection risk. `${{ github.event.pull_request.title }}` is expanded straight into the shell script, so a crafted PR title can run commands. Pass it through an environment variable instead:

```yaml
- run: echo "Title is $PR_TITLE"
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
```

If you enable Edit, or tell me to apply these another way, I'll make both changes.
