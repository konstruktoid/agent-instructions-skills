I couldn't add the stage. The Edit tool is disabled in this session, so the `Jenkinsfile` is unchanged. Here is the stage to add after the `build` stage:

```groovy
    stage('integration tests') {
      steps {
        withCredentials([string(credentialsId: 'staging-database-url', variable: 'DATABASE_URL')]) {
          sh 'python -m pytest tests --junitxml=integration-results.xml'
        }
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: 'integration-results.xml'
        }
      }
    }
```

I haven't run it, and these parts are guesses:
- **Credential:** `staging-database-url` is a placeholder ID. Create a "Secret text" credential in Jenkins with the staging connection string, or change the ID to match yours.
- **Env var:** the tests would need to read `DATABASE_URL`. Nothing in the repo currently references a database. The only match was the `postgres:17` image in `docker-compose.yml`.
- **Test command:** the only test is a unit test in `tests/test_balance.py`. There's no separate integration suite or marker. Point `pytest` at the right path or marker once you have one.
- **Agent:** the stage runs on `agent any`, so that agent needs Python, pytest and network access to staging.

The secret is bound with `withCredentials` and used in a single-quoted `sh` step. That keeps Jenkins from interpolating it into the script, and it masks the value in logs.

If you want me to write it into the file, re-enable Edit or tell me another way to write it.
