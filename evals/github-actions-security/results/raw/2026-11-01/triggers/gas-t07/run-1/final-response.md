I can't edit files in this session because I don't have a write or edit tool, so here's the change for you to paste in. A few things about the repo first:

- **There are no integration tests yet.** `tests/` only has `test_balance.py`, a unit test that never touches a database. So I've used a `pytest -m integration` marker. Unless you add tests with that marker, the stage will run nothing.
- **There's no staging database config anywhere.** The only database is the `postgres:17` service in `docker-compose.yml`, and it's local. The credential ID and environment variable names below are placeholders I made up.

Updated `Jenkinsfile`:

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
        lock(resource: 'staging-db')   // needs the Lockable Resources plugin; drop if not installed
      }
      environment {
        // Username/password credential stored in Jenkins; never hard-code these.
        STAGING_DB = credentials('staging-db-credentials')
        STAGING_DB_HOST = 'staging-db.internal'
        STAGING_DB_PORT = '5432'
        STAGING_DB_NAME = 'ledger_staging'
      }
      steps {
        // Single quotes: the shell expands the secrets, so Groovy never interpolates them into the script or the log.
        sh '''
          export DATABASE_URL="postgresql://${STAGING_DB_USR}:${STAGING_DB_PSW}@${STAGING_DB_HOST}:${STAGING_DB_PORT}/${STAGING_DB_NAME}"
          python -m pip install -e . pytest
          python -m pytest -m integration --junitxml=reports/integration.xml tests/
        '''
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

Why it's built this way:
- **`credentials()` with a single-quoted `sh`** keeps the password out of the Groovy string and out of the console log. Jenkins also masks `STAGING_DB_PSW` in the output.
- **`lock('staging-db')`** stops two builds from running against the shared staging database at once. Remove it if you don't have the Lockable Resources plugin.
- **`timeout`** stops a hung database connection from blocking the build agent forever.
- **`junit` in `post { always }`** publishes the results even when tests fail.

To finish the setup:
1. Create a Jenkins "Username with password" credential with the ID `staging-db-credentials`.
2. Set `STAGING_DB_HOST` and `STAGING_DB_NAME` to your real values.
3. Register the `integration` marker in `pytest.ini` or `pyproject.toml`, and write tests that read `DATABASE_URL`.
4. Check that `pip install -e .` works. I didn't see a `pyproject.toml` or `setup.py` among the repo's files, so you may need a different install step or `PYTHONPATH=src`.

If you'd like this stage to run only on certain branches (for example `when { branch 'main' }`), or want me to write a first integration test against `ledger`, tell me which.
