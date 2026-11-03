I can't edit files in this session (I only have read and search tools), so here's the change for you to apply to `Jenkinsfile`:

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
        lock(resource: 'staging-db')   // needs the Lockable Resources plugin; remove if not installed
      }
      environment {
        DB_HOST = 'staging-db.internal.example.com'   // replace with the real staging host
        DB_PORT = '5432'
        DB_NAME = 'ledger_staging'
      }
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'staging-db-credentials',
          usernameVariable: 'DB_USER',
          passwordVariable: 'DB_PASSWORD'
        )]) {
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

**How it's built:**
- **Credentials:** The DB username and password come from a Jenkins credential through `withCredentials`, so they aren't stored in the repo and Jenkins hides them in the logs. The shell block is in single quotes, so the shell reads `$DB_PASSWORD` at runtime and Groovy never puts the password into the command string.
- **`lock`:** Only one build at a time can run tests against staging, so parallel builds don't change the same data at once.
- **Timeout and JUnit report:** A hung DB connection can't stall the agent, and test results show up in the Jenkins UI.

**What you need to fill in, since the repo doesn't have these yet:**
1. **Integration tests:** There's no `tests/integration/` directory. The only test is a unit test in `tests/test_balance.py`. Change the path to wherever your integration tests will live.
2. **Jenkins credential:** Create a "Username with password" credential with the ID `staging-db-credentials`, or change the ID to match one you already have.
3. **DB details:** Replace the placeholder host, port and database name. I assumed Postgres because of port 5432; I didn't find a DB config in the repo to confirm that.
4. **Install step:** I didn't see a `pyproject.toml` or `setup.py`, so `pip install -e .` may fail. If you install dependencies another way (a `requirements.txt` or a `make` target), use that instead.
5. **Your tests need to read `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` and `DB_PASSWORD` from the environment.**

I couldn't run or check this pipeline here. If you tell me your credential ID, how you install dependencies and where the tests live, I can adjust it.
