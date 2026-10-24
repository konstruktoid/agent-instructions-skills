I couldn't make the change. File editing is turned off in this session and I have no shell, so the Jenkinsfile is still as it was. Here's the full file with the new stage, ready to paste in:

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
          credentialsId: 'staging-db-credentials',
          usernameVariable: 'STAGING_DB_USER',
          passwordVariable: 'STAGING_DB_PASSWORD'
        )]) {
          sh 'make integration-test'
        }
      }
    }
  }
}
```

**What the stage does:**
- **Credentials:** The database username and password come from a Jenkins credential through `withCredentials`, so Jenkins hides them in the logs. The `sh` command is in single quotes so Groovy doesn't insert the password into the script text, where it could leak.
- **`lock(resource: 'staging-db')`:** Only one build at a time can use the shared staging database, so runs don't interfere with each other's data. This needs the Lockable Resources plugin; remove the line if you don't have it.
- **`timeout`:** If the database hangs, the stage fails after 20 minutes instead of holding the agent and the lock indefinitely.

**Placeholders to fill in.** The repo has no existing setup for integration tests or a staging database, so these are my guesses:
- **Host and database name:** `staging-db.internal` and `ledger_staging` are invented. Replace them with the real values.
- **Credential:** `staging-db-credentials` needs to exist in Jenkins as a "Username with password" credential, or you can change the ID to one you already have.
- **`make integration-test`:** No Makefile is checked in, so there's no target yet; the existing `make build` must come from elsewhere. The only test is `tests/test_balance.py`, which is a unit test. If you'd rather call pytest directly, a common approach is `sh 'pytest -m integration'` with the integration tests tagged by a marker. The tests need to read `STAGING_DB_HOST`, `STAGING_DB_NAME`, `STAGING_DB_USER` and `STAGING_DB_PASSWORD` from the environment.

If you turn file editing back on, I can apply this directly, and I can also add the Makefile target and an example integration test that connects to the database.
