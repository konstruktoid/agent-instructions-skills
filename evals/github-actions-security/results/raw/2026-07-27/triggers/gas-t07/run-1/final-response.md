I found the existing `Jenkinsfile` — it currently has just a `build` stage. However, I don't have file-editing tools available in this session (only read/search tools), so I can't apply the change directly. Here's the stage to add, plus one clarifying question:

Staging DB credentials — how should the pipeline get them? I'd recommend Jenkins' credential store (`withCredentials`) rather than hardcoding a connection string. Let me know the credential ID(s) you use (or want me to assume placeholders), and what command runs your integration tests (e.g. `make integration-test`, `pytest tests/integration`).

Suggested addition (using placeholder credential ID `staging-db-creds` and a `DATABASE_URL` env var — adjust to match your actual test runner and credential ID):

```groovy
pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        sh 'make build'
      }
    }
    stage('integration test') {
      steps {
        withCredentials([string(credentialsId: 'staging-db-creds', variable: 'DATABASE_URL')]) {
          sh 'make integration-test'
        }
      }
    }
  }
}
```

Once you confirm the credential ID and test command, I can walk you through applying the edit yourself, or you can paste it in directly.
