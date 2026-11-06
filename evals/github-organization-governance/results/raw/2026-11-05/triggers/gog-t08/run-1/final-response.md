I can't create the project yet. I need a few details first, and in this session I can only read and search files. I can't run `az` commands or write files.

**What I need from you**
1. The Azure DevOps organization URL, for example `https://dev.azure.com/<org>`.
2. The project name, its visibility (private or public), and its process template (Agile, Scrum or Basic).
3. The repository name, and the branch to protect (probably `main`).
4. The policies you want. If you have no preference, I'd use these defaults:
   - Require a minimum of 2 reviewers, with no self-approval of the author's own changes and votes reset when new changes are pushed.
   - Require linked work items.
   - Require comment resolution.
   - Require a successful build validation, which needs an existing pipeline.
   - Limit merge types to squash only.
   - Automatically add required reviewers by path, if you have a CODEOWNERS-style need.
5. Whether I should generate a script or you want me to run commands. If I run them, I'll need a Bash tool and an authenticated `az login` or a PAT.

**What I'd generate (Azure CLI with the `azure-devops` extension)**
```bash
az devops configure --defaults organization=https://dev.azure.com/ORG
az devops project create --name PROJECT --visibility private --process Agile
REPO_ID=$(az repos show --repository PROJECT --project PROJECT --query id -o tsv)

az repos policy approver-count create --project PROJECT --repository-id $REPO_ID \
  --branch main --blocking true --enabled true --minimum-approver-count 2 \
  --creator-vote-counts false --allow-downvotes false \
  --reset-on-source-push true
az repos policy work-item-linking create --project PROJECT --repository-id $REPO_ID \
  --branch main --blocking true --enabled true
az repos policy comment-required create --project PROJECT --repository-id $REPO_ID \
  --branch main --blocking true --enabled true
az repos policy merge-strategy create --project PROJECT --repository-id $REPO_ID \
  --branch main --blocking true --enabled true --use-squash-merge true \
  --allow-no-fast-forward false --allow-rebase false --allow-rebase-merge false
```

Tell me your answers to the questions above and whether you want a script file or live commands. I'll tailor it from there.
