**Both `git merge` and `git rebase` combine work from one branch into another. They differ in how they treat history.**

## git merge
- Joins two branches by creating a **merge commit** with two parents.
- Existing commits are left unchanged, with their original hashes and timestamps.
- History is **non-linear**. It records exactly when and where branches diverged and rejoined.
- It is safe on shared branches because it never rewrites history.

```
A---B---C  (main)
     \   \
      D---E---M  (feature, after merging main)
```

## git rebase
- **Replays** your branch's commits on top of another base, as if you had started from the latest commit there.
- Each replayed commit is a **new commit** with a new hash, so history is rewritten.
- History is **linear**, with no merge commit, which makes `git log` easier to read.
- Conflicts are resolved commit by commit, so you may have to resolve several times.

```
Before:        A---B---C  (main)
                    \
                     D---E  (feature)

After rebase:  A---B---C---D'---E'  (feature)
```

## Key tradeoffs

| | Merge | Rebase |
|---|---|---|
| History | Preserved, non-linear | Rewritten, linear |
| Extra commit | Yes (merge commit) | No |
| Commit hashes | Unchanged | Changed |
| Safe on shared branches | Yes | No |
| Conflict resolution | Once | Possibly per commit |
| Undo | Easy (`git revert -m`) | Harder (reflog) |

## Rules of thumb
- **Rebase** local, unpublished branches to tidy history or to pick up upstream changes before opening a PR.
- **Merge** when integrating shared or public branches, or when you want to keep a record of the integration.
- **Never rebase commits others have based work on.** Rewriting published history forces collaborators to reconcile diverged copies. If you do rebase a branch you've already pushed, you'll need `git push --force-with-lease`.

A common workflow is to rebase your feature branch onto `main` while you work. Then merge it into `main` through a PR, using a merge commit or a squash.
