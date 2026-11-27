I can't save files in this session because I only have read and search tools here. Below is the stage to paste into the `Jenkinsfile`.

The current `Jenkinsfile` has just one stage, `build` (`sh 'make build'`). There's no `tests/integration/` directory yet; `tests/test_balance.py` is the only test. So the test path, credential ID and environment variable names below are placeholders you'll need to change.

```groovy
pipeline {
  agent any
  options {
    timeout(time: 30, unit: 'MINUTES')
  }
  stages {
    stage('build') {
      steps {
        sh 'make build'
      }
    }

    stage('integration tests (staging DB)') {
      // Only run on trusted branches, so PR builds from forks can't read staging credentials
      when {
        anyOf {
          branch 'main'
          branch 'release/*'
        }
      }
      // Stop two builds from writing to the shared staging DB at the same time
      // (needs the Lockable Resources plugin; remove if you don't have it)
      options {
        lock(resource: 'staging-db')
      }
      environment {
        STAGING_DB_HOST = 'staging-db.internal.example.com'
        STAGING_DB_PORT = '5432'
        STAGING_DB_NAME = 'ledger_staging'
      }
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'staging-db-credentials',
          usernameVariable: 'STAGING_DB_USER',
          passwordVariable: 'STAGING_DB_PASSWORD'
        )]) {
          // Single quotes: the shell expands the secrets, so Groovy never puts them in the build log
          sh '''
            python -m pip install -e . pytest
            PYTHONPATH=src python -m pytest tests/integration \
              --junitxml=reports/integration.xml
          '''
        }
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: 'reports/integration.xml'
        }
      }
    }
  }
}
```

Why it's set up this way:
- **The database password stays out of the logs.** It comes from the Jenkins credentials store through `withCredentials`, which also hides it if it's printed. The `sh` block uses single quotes so Groovy doesn't insert the secret into the command text.
- **Only trusted branches get the credentials.** The `when` condition keeps pull request builds (including from forks) from running code that could read them.
- **Builds take turns on staging.** The `lock` stops two builds from writing to the shared staging database at once. It needs the Lockable Resources plugin, so remove it if you don't have that.
- **Results appear in Jenkins.** The `junit` step publishes the test report, and `allowEmptyResults: true` stops it from failing the build when no integration tests exist yet.

Before you merge, you'll need to:
1. Create a username/password credential called `staging-db-credentials` in Jenkins, or change the ID.
2. Replace the host and database name with your real staging values.
3. Add tests under `tests/integration/` that read `STAGING_DB_*` from the environment and clean up any data they create.
4. Check that the install command fits your setup. There's no `pyproject.toml` or Makefile test target in the workspace, so if `make build` already sets up the environment, change the `sh` lines to use it.

If you tell me your real branch names, credential ID and how you run tests, I can adjust it.
