I don't have file-editing tools available in this session (only Read/Glob/Grep/Skill), so I can't write the change directly. Here's the updated `Jenkinsfile` content for you to apply — it uses Jenkins credential binding so the staging DB connection string is never exposed in plaintext or logs:

```groovy
pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        sh 'make build'
      }
    }
    stage('integration-test') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'staging-db',
          usernameVariable: 'STAGING_DB_USER',
          passwordVariable: 'STAGING_DB_PASSWORD'
        )]) {
          sh 'make integration-test'
        }
      }
    }
  }
}
```

Notes:
- `withCredentials` pulls the staging DB user/password from a Jenkins credential (`staging-db`) — set that up in the Jenkins credentials store rather than hardcoding values here. Jenkins also masks these values in the console log automatically.
- I assumed a `make integration-test` target that reads `STAGING_DB_USER`/`STAGING_DB_PASSWORD` (plus whatever host/port/db name env vars you already use) to connect — there's no existing Makefile in this repo, so you'll need to add that target, or tell me the actual test command (e.g. `pytest tests/integration`) and I'll adjust the `sh` step to match.
- Consider restricting this stage to specific branches (e.g. `when { branch 'main' }`) if you don't want every build/PR hitting the shared staging database.

Let me know if you'd like me to also add the `integration-test` Makefile target or adjust the test command.
