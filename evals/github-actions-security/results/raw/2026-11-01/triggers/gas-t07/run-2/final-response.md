I can't edit files in this session because I only have read and search tools, not write or edit. Here is the full updated `Jenkinsfile` for you to paste in.

```groovy
pipeline {
  agent any

  options {
    // Only one run at a time touches the shared staging database
    disableConcurrentBuilds()
    timeout(time: 30, unit: 'MINUTES')
  }

  stages {
    stage('build') {
      steps {
        sh 'make build'
      }
    }

    stage('integration tests (staging DB)') {
      // Keep untrusted branches/PRs away from staging credentials
      when {
        branch 'main'
      }
      environment {
        // Jenkins "Secret text" credential holding e.g.
        // postgresql://ledger_ci:<password>@staging-db.internal:5432/ledger
        STAGING_DATABASE_URL = credentials('staging-db-url')
        PYTHONPATH           = "${env.WORKSPACE}/src"
      }
      steps {
        sh '''
          set -eu
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --quiet pytest
          mkdir -p reports
          pytest -m integration tests/ --junitxml=reports/integration.xml
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

**Before it will work:**

1. **The credential:** create a Jenkins "Secret text" credential with the ID `staging-db-url` holding the staging connection string, or change the ID in the file. Jenkins hides the value in the build log. Use a dedicated CI database account that only has access to what the tests need, not an admin login.
2. **The tests:** this repo has no integration tests yet. `tests/test_balance.py` is a plain unit test, and nothing in `src/ledger/` connects to a database. The stage runs tests marked with `@pytest.mark.integration` that read `STAGING_DATABASE_URL`. Until some exist, pytest finds no tests and exits with code 5, which fails the stage. You'll also want to register the `integration` marker in `pytest.ini` or `pyproject.toml`.
3. **Branch filter:** I limited the stage to `main` so that builds of other branches or pull requests can't use the staging credentials. If your default branch has a different name, or you want this on release branches too, change the `when` block.
4. **Dependencies:** the stage only installs `pytest`. If the project has a requirements file or you need a database driver such as `psycopg`, add it to the `pip install` line.

Since several pipeline runs share one staging database, the tests should create and clean up their own data, for example by using unique prefixes or wrapping each test in a transaction that gets rolled back. `disableConcurrentBuilds()` stops two runs of this job from overlapping, but it doesn't protect against other jobs or people using the same database.
