I couldn't edit the file because this session only has read and search tools. Here is the complete updated `Jenkinsfile` for you to paste in:

```groovy
pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        sh 'make build'
      }
    }
    stage('integration tests (staging DB)') {
      options {
        timeout(time: 20, unit: 'MINUTES')
        lock(resource: 'staging-db')   // needs the Lockable Resources plugin
      }
      environment {
        STAGING_DB_HOST = 'staging-db.internal.example'   // replace with the real host
        STAGING_DB_NAME = 'ledger_staging'                 // replace with the real database name
      }
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'staging-db-credentials',
          usernameVariable: 'STAGING_DB_USER',
          passwordVariable: 'STAGING_DB_PASSWORD'
        )]) {
          // Single quotes: the shell expands the secrets, not Groovy, so they stay masked
          sh '''
            python -m pip install -e . pytest
            python -m pytest tests/integration --junitxml=reports/integration.xml
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

**Why it's set up this way:**
- **Credentials:** the stage reads the database login from a Jenkins credential (`staging-db-credentials`) and only exposes it inside `withCredentials`. Nothing is hardcoded. Single quotes around the `sh` block mean the shell fills in the password, not Groovy, so Jenkins keeps it masked in the logs.
- **`lock`:** this stops two builds from running against the shared staging database at the same time. You need the Lockable Resources plugin for it. If you don't have the plugin, delete that line.
- **Timeout and test report:** the timeout stops a hung database connection from blocking the agent. The `junit` step publishes the results even when tests fail.

**Things you need to fill in:**
1. **Tests:** there are no integration tests in the repo yet. `tests/` only has a unit test (`tests/test_balance.py`), so I pointed the stage at `tests/integration/`. Change the path or use a pytest marker (`-m integration`) to match how you want to organise them.
2. **Database settings:** nothing in the code reads database settings yet. `src/ledger/client.py` only takes a transport function. The tests will need to read `STAGING_DB_HOST`, `STAGING_DB_NAME`, `STAGING_DB_USER` and `STAGING_DB_PASSWORD` from the environment, or you can rename those variables to whatever your code expects.
3. **Jenkins setup:** create the `staging-db-credentials` credential in Jenkins as a username and password. Then replace the placeholder host and database name.

If you want this stage to run only on certain branches, such as `main`, add `when { branch 'main' }` to the stage.
