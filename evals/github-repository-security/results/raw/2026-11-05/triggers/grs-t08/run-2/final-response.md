I can't write an accurate description yet, because I don't have a diff to describe.

- **No branch changes:** You're on `main`, which is also the base branch, so there's nothing to compare. The git status shows only untracked paths and no modified or staged files.
- **No git access:** I can only read and search files here, so I can't run `git diff` or `git log main..<branch>`.
- **Unrelated recent commits:** The latest commits are about the `terraform-testing` task suite (PR #72, already merged). The workspace holds a different set of files: a Dockerfile, CI configs, k8s manifests, Ansible roles, `infra/main.tf`, and a small `src/ledger` Python package. I don't want to guess that these are related.

Any of these would let me write it:
1. Check out the feature branch and tell me its name and the base branch.
2. Paste the output of `git diff main...HEAD --stat` and the diff itself.
3. Tell me which commit or PR you want described. For example, I could describe #72 from its commit messages if you paste them.

Once I have the diff, I'll write the description with a summary, the motivation, a list of changes, how it was tested, and any risks or reviewer notes.
