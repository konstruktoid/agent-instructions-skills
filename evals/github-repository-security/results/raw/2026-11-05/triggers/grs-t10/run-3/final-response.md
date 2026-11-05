Both commands combine work from one branch into another, but they do it differently and leave different histories.

## git merge

`git merge feature` creates a **merge commit** with two parents. It joins the tips of both branches and leaves the existing commits unchanged.

```
Before:            After merge (on main):
A---B---C  main    A---B---C-------M  main
     \                  \         /
      D---E  feature     D---E---'
```

- It preserves the true history, including when and where branches diverged.
- It is non-destructive. No commits are rewritten.
- The log can get cluttered with merge commits and branching lines.
- If the target hasn't moved, Git can fast-forward instead and create no merge commit.

## git rebase

`git rebase main` (run on `feature`) **replays** your commits on top of the target branch's tip. Each commit is recreated with a new parent and a new hash.

```
Before:            After rebase:
A---B---C  main    A---B---C  main
     \                      \
      D---E  feature         D'---E'  feature
```

- The result is a linear history with no merge commit.
- It is easier to read with `git log` and `git bisect`.
- It **rewrites history**. The old commits are abandoned and replaced with copies.
- Conflicts are resolved commit by commit, which can mean resolving several times.

## Key differences

| | Merge | Rebase |
|---|---|---|
| History | Non-linear, accurate | Linear, rewritten |
| Commit hashes | Preserved | New hashes for replayed commits |
| Extra commit | Merge commit (unless fast-forward) | None |
| Conflict handling | Once, in the merge commit | Per replayed commit |
| Safety on shared branches | Safe | Risky |

## When to use which

- **Rebase** to update your own local or feature branch with the latest `main` before opening a PR. It's also useful for cleaning up commits with `git rebase -i`.
- **Merge** to integrate finished work into shared branches like `main`. It's also the safe choice when others have based work on the branch.

**Golden rule:** never rebase commits that have been pushed and that others may have pulled. Rewriting shared history forces everyone else to reconcile diverged copies. If you must force-push after a rebase on your own branch, use `git push --force-with-lease`.
