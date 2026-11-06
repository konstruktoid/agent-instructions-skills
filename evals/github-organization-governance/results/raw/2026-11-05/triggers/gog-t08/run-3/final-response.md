I can't run anything against Azure DevOps from this session. I only have file search and read tools, and no shell or `az` access. The GitHub organization governance skill doesn't cover Azure DevOps, so I didn't use it. Below is a script you can run yourself, followed by a few questions.

```bash
ORG=https://dev.azure.com/<your-org>
PROJECT=<project-name>
REPO=$PROJECT            # default repo takes the project name
BRANCH=main

az devops configure -d organization=$ORG

# 1. Project
az devops project create --name "$PROJECT" --visibility private \
  --source-control git --process Agile

REPO_ID=$(az repos show --repository "$REPO" --project "$PROJECT" --query id -o tsv)

# 2. Minimum reviewers
az repos policy approver-count create --project "$PROJECT" \
  --repository-id $REPO_ID --branch $BRANCH \
  --minimum-approver-count 2 --creator-vote-counts false \
  --reset-on-source-push true --allow-downvotes false \
  --blocking true --enabled true

# 3. Linked work items required
az repos policy work-item-linking create --project "$PROJECT" \
  --repository-id $REPO_ID --branch $BRANCH --blocking true --enabled true

# 4. Comment resolution required
az repos policy comment-required create --project "$PROJECT" \
  --repository-id $REPO_ID --branch $BRANCH --blocking true --enabled true

# 5. Squash merge only
az repos policy merge-strategy create --project "$PROJECT" \
  --repository-id $REPO_ID --branch $BRANCH \
  --allow-squash true --allow-no-fast-forward false \
  --allow-rebase false --allow-rebase-merge false \
  --blocking true --enabled true

# 6. Build validation (needs an existing pipeline)
az repos policy build create --project "$PROJECT" \
  --repository-id $REPO_ID --branch $BRANCH \
  --build-definition-id <pipeline-id> --display-name "CI" \
  --queue-on-source-update-only false --manual-queue-only false \
  --valid-duration 720 --blocking true --enabled true

# Verify by reading the applied state back
az repos policy list --project "$PROJECT" --branch $BRANCH -o table
```

I need these from you to tailor it:
1. What are your organization and project names?
2. Which branches need policies? Just `main`, or also `release/*`?
3. What reviewer count do you want, and do you need a required-reviewer group or path-based reviewers?
4. Is there a CI pipeline for build validation yet?
5. Do you want me to write this to a script file in the workspace, or would you prefer Terraform with the `azuredevops` provider?

Running this creates resources in your Azure DevOps organization, so run it yourself or confirm first. It also needs `az extension add --name azure-devops` and `az devops login` with a PAT that has project-creation and policy-management rights.
