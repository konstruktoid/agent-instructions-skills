The GitHub governance skill doesn't apply here, since this is Azure DevOps, so I'm working from the `az devops` CLI directly. I haven't run anything yet, because I need your organization details and your approval before changing anything outward-facing. Here is the setup I'd run.

```bash
ORG="https://dev.azure.com/<your-org>"
PROJECT="<project-name>"
REPO="$PROJECT"
BRANCH="main"

az login
az devops configure --defaults organization="$ORG"

# 1. Project (private, git, agile process)
az devops project create --name "$PROJECT" \
  --visibility private --source-control git --process Agile

REPO_ID=$(az repos show --repository "$REPO" --project "$PROJECT" --query id -o tsv)
COMMON="--project $PROJECT --repository-id $REPO_ID --branch $BRANCH --blocking true --enabled true"

# 2. Minimum reviewers (2, creator can't self-approve, reset votes on new pushes)
az repos policy approver-count create $COMMON \
  --minimum-approver-count 2 --creator-vote-counts false \
  --allow-downvotes false --reset-on-source-push true

# 3. Linked work items required
az repos policy work-item-linking create $COMMON

# 4. Comment resolution required
az repos policy comment-required create $COMMON

# 5. Merge strategy: squash only
az repos policy merge-strategy create $COMMON \
  --use-squash-merge true --allow-no-fast-forward false \
  --allow-rebase false --allow-rebase-merge false

# 6. Build validation (needs an existing pipeline)
# az repos policy build create $COMMON --build-definition-id <id> \
#   --display-name "PR build" --queue-on-source-update-only false \
#   --manual-queue-only false --valid-duration 720
```

Two settings can't be done through these commands:
- **Permissions:** deny "Bypass policies when pushing" and "Bypass policies when completing pull requests" for Contributors. Use `az devops security permission update`, or the repo's Security tab.
- **Required reviewer groups or paths:** add these with `az repos policy required-reviewer create`.

Before I run this, I need to know:
1. The organization URL and the project name. Is the project new or does it already exist?
2. Should the policies cover only `main`, or also `release/*`? Branch policies can target a prefix.
3. Is there an existing pipeline for build validation?
4. Do you want a different reviewer count or merge strategy than the ones above?

Once you confirm, I'll run it and then read the policies back with `az repos policy list` to check they applied.
