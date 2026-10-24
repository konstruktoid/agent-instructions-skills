I couldn't change the `Jenkinsfile` because this session can only read files, not write them. Here's the stage to paste in. Nothing has been run or tested.

**`Jenkinsfile`** (the new stage goes after `build`):

```groovy
pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        sh 'make build'
      }
    }
    stage('integration-test') {
      environment {
        STAGING_DB_HOST = 'staging-db.internal'
        STAGING_DB_NAME = 'ledger_staging'
      }
      options {
        timeout(time: 20, unit: 'MINUTES')
        lock(resource: 'staging-db')
      }
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'staging-db',
          usernameVariable: 'STAGING_DB_USER',
          passwordVariable: 'STAGING_DB_PASSWORD'
        )]) {
          sh '''
            export DATABASE_URL="postgresql://${STAGING_DB_USER}:${STAGING_DB_PASSWORD}@${STAGING_DB_HOST}:5432/${STAGING_DB_NAME}"
            python -m pytest tests/integration -m integration --junitxml=reports/integration.xml
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
- **Credentials come from Jenkins, not the file.** `withCredentials` pulls them from a credential with the ID `staging-db`, and Jenkins hides them in the console log.
- **Single quotes around the `sh` block.** The shell fills in the password, not Groovy. Groovy-style `"${...}"` with a secret would leak it into the build log, and Jenkins warns about this.
- **`lock(resource: 'staging-db')`** stops two builds from running tests against the shared staging database at once. It needs the Lockable Resources plugin. If you don't have it, remove that line.
- **`timeout`** keeps a stuck database connection from blocking the agent indefinitely.
- **Postgres URL**, matching the `postgres:17` service in `docker-compose.yml`.

**Things to check before merging:**
1. **The repo has no integration tests yet.** The only test is `tests/test_balance.py`, a unit test that doesn't use a database. I guessed `tests/integration` and a pytest `integration` marker. Change these to wherever your tests will live.
2. **I don't know how your tests connect to the database.** I made up `DATABASE_URL`, and the host and database name are placeholders. Use whatever your tests actually read.
3. **Create the `staging-db` credential in Jenkins** as a "Username with password" credential, scoped to this job or folder.
4. **There's no Makefile in the repo**, though `build` already runs `make build`. If you'd rather keep commands in `make`, add a `make integration-test` target and call that instead of pytest.
5. **Data written to staging stays there.** If the tests write data, they should clean up after themselves or use a dedicated schema per run.

If you enable file editing, I can apply this directly and adjust it to your test layout.
