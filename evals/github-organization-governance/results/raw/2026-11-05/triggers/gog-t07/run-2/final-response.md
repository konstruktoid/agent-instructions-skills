I couldn't edit `.github/workflows/deploy.yml`. The Edit tool is disabled in this session, so the file is unchanged.

The change I would make is to replace line 7:

```yaml
permissions: write-all
```

with:

```yaml
permissions:
  contents: read
```

The `deploy` job only runs `actions/checkout` and an `echo`, so read access to contents is all it needs. `write-all` gives the `GITHUB_TOKEN` write access to everything, and this workflow runs on `pull_request`.

There is a separate problem on line 14. `${{ github.event.pull_request.title }}` is interpolated straight into the shell command, so a crafted PR title could inject commands. The fix is to pass it through an environment variable:

```yaml
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: echo "Title is $PR_TITLE"
```

I haven't changed this because you only asked about permissions. It's worth doing, though, because it limits what the injection could reach.

If you'd like me to apply both changes, enable editing or tell me another way to write the file.
