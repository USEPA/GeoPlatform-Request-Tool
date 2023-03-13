// abort existing build
def buildNumber = env.BUILD_NUMBER as int
if (buildNumber > 1) milestone(buildNumber - 1)
milestone(buildNumber)

node('staging') {
    try {
        configFileProvider([
            configFile(fileId: 'a9ed1374-1437-4d32-9593-094073a48bca', variable: 'APP_ROOT'),
            configFile(fileId: 'a9ed1374-1437-4d32-9593-094073a48bca', variable: 'NOTIFICATION_CHANNEL_ID')
            configFile(fileId: 'a9ed1374-1437-4d32-9593-094073a48bca', variable: 'VENV_ACTIVATE_CMD')
            configFile(fileId: 'a9ed1374-1437-4d32-9593-094073a48bca', variable: 'NPM_PATH')
        ]) {
            dir('$APP_ROOT') {
                checkout scm
                stage('update backend dependencies') {
                    bat "$VENV_ACTIVATE_CMD && pip install -r requirements.txt"
                }
                // need permissions to create test db
        //         stage('run backend test') {
        //             bat ".\\venv\\Scripts\\activate && python manage.py test --noinput"
        //         }
                stage('run migrations') {
                    bat "$VENV_ACTIVATE_CMD && python manage.py migrate"
                }

                dir('.\\ui') {
                    stage('update frontend dependencies') {
                        bat "$NPM_PATH\\npm i"
                    }
                    stage("build frontend") {
                        bat "$NPM_PATH\\npm run build:ngst-staging"
                    }
                }
           }
            stage("Approval") {
                slackSend(channel:'$NOTIFICATION_CHANNEL_ID', message: "Account Request Tool Staging Build COMPLETE")
                input(message: "Approved for merge?")
                // todo: revert migrations on abort
            }

        }
  } catch(Exception e) {
      slackSend(channel:'$NOTIFICATION_CHANNEL_ID', message: "Account Request Tool Staging Build FAILED or SUPERSEDED")
      slackSend(channel:'$NOTIFICATION_CHANNEL_ID', message: e)
    }
}
