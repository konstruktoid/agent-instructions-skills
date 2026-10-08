I couldn't add the stage because the Edit tool is disabled in this session, so the Jenkinsfile is unchanged. This is the change I would have made. Add it after the `build` stage:

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
          sh 'make integration-test'
        }
      }
    }
  }
}
```

I made two assumptions, because the repo has no Makefile and nothing that mentions integration tests:
- **Test command:** `make integration-test` is a guess. Replace it with your real command.
- **Credentials:** `staging-db-url` is a placeholder Jenkins credential ID, a secret-text credential holding the staging connection string. The tests read it as `DATABASE_URL`. Rename both to match your setup.

Jenkins masks the secret in the console log.

If you enable Edit or ask me to write the file another way, I'll apply it.
