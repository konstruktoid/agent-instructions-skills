I can't edit files in this session because I only have read and search tools. Here's the updated `Jenkinsfile` for you to paste in:

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
      }
      environment {
        PYTHONPATH = "${WORKSPACE}/src"
      }
      steps {
        withCredentials([string(credentialsId: 'staging-db-url', variable: 'DATABASE_URL')]) {
          sh '''
            python3 -m pip install --quiet pytest psycopg[binary]
            python3 -m pytest tests/integration --junitxml=reports/integration.xml
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

**How it works:**
- **Credentials:** The connection string comes from a Jenkins credential, so it's never written in the repo. The `sh` block uses single quotes on purpose. That way the shell reads `$DATABASE_URL` and Groovy never sees it, which avoids Jenkins' warning about secrets in Groovy strings and keeps the value masked in logs.
- **Timeout:** If the staging database hangs, the stage stops after 20 minutes instead of holding the build agent.
- **Test results:** `junit` publishes the results even when the tests fail.

**Things you'll need to set up or change:**
1. **The credential.** Create a "Secret text" credential with the ID `staging-db-url` holding something like `postgresql://user:pass@staging-host:5432/ledger`, or change the ID to match one you already have. Give it a staging-only user with the fewest permissions that work.
2. **The tests.** The repo has no integration tests yet; only `tests/test_balance.py` exists, and it's a unit test. The stage expects them in `tests/integration/` and reading `DATABASE_URL`. If you'd rather use a pytest marker, change the command to `pytest -m integration`.
3. **The Postgres driver.** I picked `psycopg` because `docker-compose.yml` uses `postgres:17`. If you have a requirements file, install from that instead.
4. **Which builds run it (optional).** To run it only on `main`, so other branches and PR builds can't reach staging, add `when { branch 'main' }` to the stage.
