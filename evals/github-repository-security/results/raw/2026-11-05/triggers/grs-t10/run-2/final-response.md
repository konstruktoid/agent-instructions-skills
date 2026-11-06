**Git merge** and **git rebase** both integrate changes from one branch into another, but they do it differently and produce different histories.

## Git merge

`git merge feature` (run from `main`) creates a new **merge commit** with two parents. It joins the two lines of history together.

```
A---B---C---------M   main
     \           /
      D---E---F       feature
```

- Existing commits are left unchanged.
- History shows what happened, including when branches diverged and joined.
- The history can get cluttered with many merge commits.
- It is safe on shared branches, because nothing is rewritten.

## Git rebase

`git rebase main` (run from `feature`) takes your branch's commits and **replays them on top of** the target branch's tip. Each replayed commit is a new commit with a new hash.

```
A---B---C           main
         \
          D'---E'---F'   feature
```

- History becomes linear, with no merge commit.
- The original commits are rewritten, so their hashes change.
- You may have to resolve conflicts once per replayed commit.
- `git rebase -i` also lets you squash, reorder, or edit commits.

## Key differences

| | Merge | Rebase |
|---|---|---|
| History | Non-linear, preserves true history | Linear, rewritten |
| Commits | Originals kept, plus a merge commit | Commits recreated with new hashes |
| Conflicts | Resolved once | Possibly resolved per commit |
| Safety on shared branches | Safe | Risky, because it rewrites history |
| Traceability | Shows when and how branches joined | Hides the branching context |

## When to use which

- **Rebase** to update your own local or feature branch with the latest `main` before opening a PR. It keeps history clean.
- **Merge** to bring a finished feature into `main`, or on any branch others have pulled.
- **Golden rule:** never rebase commits that you have already pushed to a shared branch. Rewriting them forces collaborators to reconcile diverged history. If you must push a rebased branch, use `git push --force-with-lease`, and only on a branch that is yours alone.

A common workflow is to rebase your feature branch onto `main` while you work, then merge it into `main` when it's done.
