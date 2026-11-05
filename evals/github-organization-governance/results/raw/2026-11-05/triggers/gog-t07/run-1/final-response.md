I couldn't edit `.github/workflows/deploy.yml` because the Edit tool is disabled in this session. The change is small, so you can apply it by hand.

Replace line 7:

```yaml
permissions: write-all
```

with:

```yaml
permissions:
  contents: read
```

The job only runs `actions/checkout` and an `echo`. Checkout needs only `contents: read`, so nothing in the workflow needs write access. Every other scope is set to `none` once you declare the block.

There is a separate problem on line 14. `${{ github.event.pull_request.title }}` is interpolated straight into the shell script, so a PR title can inject commands. I'd pass it through an environment variable instead:

```yaml
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: echo "Title is $PR_TITLE"
```

I haven't changed that either. I can apply both edits if you enable editing or ask me to use a different route.
