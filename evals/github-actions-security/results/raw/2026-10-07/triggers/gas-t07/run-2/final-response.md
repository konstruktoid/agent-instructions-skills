I couldn't add the stage. The Edit tool is disabled in this session, and I have no other way to modify files here, so the `Jenkinsfile` is unchanged.

This is the stage I would add after `build`:

```groovy
    stage('integration tests') {
      steps {
        withCredentials([string(credentialsId: 'staging-database-url', variable: 'DATABASE_URL')]) {
          sh 'make integration-test'
        }
      }
    }
```

I had to guess two things, and the repo doesn't show either one:
- **Credential ID:** `staging-database-url` is a placeholder. It needs to be a Jenkins credential that holds the staging connection string. Keeping it there means the connection string never appears in the repo or the logs.
- **Test command:** `make integration-test` is a guess, matching the existing `make build`. I found no integration tests or Makefile targets in the repo.

If you enable Edit or tell me to apply the change another way, I'll make it. If you give me the real credential ID and test command, I'll use those.
