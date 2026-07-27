I only have read-only tools available in this session (no Edit/Write/Bash), so I can't apply the change directly. Here's the stage to add to your `Jenkinsfile` — it uses Jenkins credentials binding so the staging DB connection string never appears in plaintext or logs:

```groovy
pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        sh 'make build'
      }
    }
    stage('integration tests') {
      steps {
        withCredentials([string(credentialsId: 'staging-db-url', variable: 'DATABASE_URL')]) {
          sh 'pytest tests/ -m integration'
        }
      }
    }
  }
}
```

Notes:
- `staging-db-url` should be a Jenkins credential (Secret text) holding the staging DB connection string — create it in Jenkins credentials store, not in the repo.
- I assumed `pytest` and a `-m integration` marker since that's the only test suite in this repo (`tests/test_balance.py`); adjust the command/marker if your integration tests live elsewhere or use a different runner.

Want me to apply this edit once write access is available, or would you like to paste it in yourself?
