I couldn't make the edit because I only have read and search tools in this session. Here is the change to make by hand. In `Jenkinsfile`, add this stage after `build`:

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
      // Only trusted branches get the staging credentials, not PR or fork builds
      when { branch 'main' }
      options { timeout(time: 20, unit: 'MINUTES') }
      environment {
        STAGING_DB_HOST = 'staging-db.internal'   // replace with your host
        STAGING_DB_NAME = 'ledger_staging'        // replace with your db name
      }
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'staging-db',
          usernameVariable: 'STAGING_DB_USER',
          passwordVariable: 'STAGING_DB_PASSWORD'
        )]) {
          // Single quotes: the shell expands the secrets, so they stay out of the Groovy string and the build log
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

**Before it will run:**
- **Create the credential:** add a "Username with password" credential with the ID `staging-db` in Jenkins.
- **Write the tests:** the repo has no integration tests yet. `tests/test_balance.py` is the only test and it's a unit test. The stage expects tests in `tests/integration/` that read the `STAGING_DB_*` environment variables to connect. There's also no `Makefile` or `pyproject.toml`, so `make build` and `pip install -e .` will fail as things stand. Change those two commands to match how the project is actually built.
- **Fill in the placeholders:** the host and database name are made up. Replace them with your real values.

**Choices I made:**
- **Main branch only:** the `when { branch 'main' }` line means pull request builds can't reach the staging database or its credentials. Remove it if you want the stage on every branch.
- **Parallel builds:** if two builds could run at once against the same staging database, wrap the steps in `lock('staging-db') { ... }`. This needs the Lockable Resources plugin.
