I can't edit files in this session because I only have read and search tools here. Below is the stage to paste into `Jenkinsfile`.

**Assumptions to check before using it:**
- **Test command:** the tests are Python (`tests/`, `src/ledger/`), but I couldn't find any existing test command or integration-test marker. I've used `pytest -m integration`. Change it if your suite runs another way.
- **Credentials:** a Jenkins credential with the ID `staging-db-url` holds the staging database connection string. That ID is a placeholder, so swap in your real one.
- **Environment variable:** the tests read the database URL from `DATABASE_URL`. I didn't confirm this against `src/ledger/client.py`.

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
      options {
        timeout(time: 20, unit: 'MINUTES')
        lock(resource: 'staging-db')   // only one run uses staging at a time
      }
      steps {
        withCredentials([string(credentialsId: 'staging-db-url', variable: 'DATABASE_URL')]) {
          // single quotes: the shell expands the secret, so Groovy never puts it into the command string
          sh '''
            python -m pip install -e . pytest
            python -m pytest -m integration tests/ --junitxml=reports/integration.xml
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

**Design choices:**
- **Credentials:** `withCredentials` keeps the staging database URL out of the Jenkinsfile and masks it in the build logs. The `sh` block uses single quotes on purpose: double quotes would let Groovy fill in the secret, which leaks it and triggers Jenkins's security warning.
- **Locking:** the `lock` step stops parallel builds from clashing on the shared staging data. It needs the Lockable Resources plugin; remove that line if you don't have it.
- **Timeout and results:** the timeout stops a hung database connection from tying up an executor. The `junit` step shows test results in Jenkins even when the stage fails.

You might also want to run this stage only on the main branch or on merges, so that builds from feature branches and pull requests can't reach staging or its credentials. To do that, add `when { branch 'main' }` to the stage.
