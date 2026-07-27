I don't have write/edit tools available in this session (only Glob, Grep, Read, and Skill are exposed), so I can't apply the change myself. Here's the stage to add to `Jenkinsfile` — you can paste it in after the `build` stage:

```groovy
pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        sh 'make build'
      }
    }
    stage('integration-tests') {
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
- `staging-db` should be a Jenkins credential (username/password type) pointing at the staging database — don't hardcode host/creds in the Jenkinsfile itself.
- `make integration-test` is a placeholder; point it at whatever target/script actually runs your integration suite, reading `STAGING_DB_USER`/`STAGING_DB_PASSWORD` (plus a staging host, likely from a non-secret env var or Jenkins config) to connect.

If you'd like, tell me the actual integration-test command and staging DB connection details (or re-grant write access) and I'll apply the edit directly.
