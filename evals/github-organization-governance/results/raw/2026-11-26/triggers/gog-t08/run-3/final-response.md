I didn't change anything. I don't have a shell in this session, so I can't run the Azure CLI or call the Azure DevOps API. I also couldn't find any Azure DevOps setup in this repo. The CI and deploy files here are for GitHub Actions (`.github/workflows/deploy.yml`), GitLab (`.gitlab-ci.yml`) and Jenkins (`Jenkinsfile`). The GitHub organization governance skill only covers GitHub, so I didn't use it.

Below is a script you can run with the `azure-devops` extension of the Azure CLI. The values marked "fill in" are ones only you know.

```bash
# Prereqs: az login; az extension add --name azure-devops
ORG="https://dev.azure.com/<your-org>"      # fill in
PROJECT="<project-name>"                    # fill in
REPO="<repo-name>"                          # fill in (defaults to project name on creation)
BRANCH="main"

az devops configure --defaults organization="$ORG"

# 1. Project (Git, Agile process, private)
az devops project create --name "$PROJECT" --source-control git \
  --process Agile --visibility private

REPO_ID=$(az repos show --project "$PROJECT" --repository "$REPO" --query id -o tsv)

# 2. Branch policies on main
# Minimum 2 reviewers, reset votes on new pushes, author can't approve own PR
az repos policy approver-count create --project "$PROJECT" --repository-id "$REPO_ID" \
  --branch "$BRANCH" --blocking true --enabled true \
  --minimum-approver-count 2 --creator-vote-counts false \
  --allow-downvotes false --reset-on-source-push true

# Linked work item required
az repos policy work-item-linking create --project "$PROJECT" --repository-id "$REPO_ID" \
  --branch "$BRANCH" --blocking true --enabled true

# All PR comments must be resolved
az repos policy comment-required create --project "$PROJECT" --repository-id "$REPO_ID" \
  --branch "$BRANCH" --blocking true --enabled true

# Squash merge only (linear history)
az repos policy merge-strategy create --project "$PROJECT" --repository-id "$REPO_ID" \
  --branch "$BRANCH" --blocking true --enabled true \
  --allow-squash true --allow-no-fast-forward false --allow-rebase false --allow-rebase-merge false

# Build validation (needs an existing pipeline ID)
# az repos policy build create --project "$PROJECT" --repository-id "$REPO_ID" \
#   --branch "$BRANCH" --blocking true --enabled true \
#   --build-definition-id <PIPELINE_ID> --display-name "PR build" \
#   --queue-on-source-update-only true --manual-queue-only false --valid-duration 720

# 3. Check what was actually applied
az repos policy list --project "$PROJECT" --repository-id "$REPO_ID" --branch "$BRANCH" -o table
```

To fit this to your setup and run it, I need:
1. **Organization URL**, **project name** and **repo name**. Also, is the project new or does it already exist?
2. **Which policies you want.** The script defaults to 2 reviewers, a linked work item, resolved comments and squash-only merges. You might also want build validation (which needs a pipeline ID), automatically added required reviewers per path, or policies on `release/*` branches.
3. **Whether to also set up a build pipeline.** The repo already has CI for GitHub Actions, GitLab and Jenkins. I could write an `azure-pipelines.yml` (the Azure Pipelines config file), for example running `tests/test_balance.py`, to use for build validation.

Once you can give me a shell, I can run the script and read back the policy list to confirm the settings.
