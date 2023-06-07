// abort existing build
def buildNumber = env.BUILD_NUMBER as int
if (buildNumber > 1) milestone(buildNumber - 1)
milestone(buildNumber)

node('staging') {
    configFileProvider([
        configFile(fileId:'a9ed1374-1437-4d32-9593-094073a48bca', variable:'CONFIG')
    ]) {
        def props = readProperties file: "$CONFIG"
        try {
            dir(props.APP_ROOT) {
                checkout scm
                stage('update backend dependencies') {
                    bat "$props.VENV_ACTIVATE_CMD && pip install -r requirements.txt"
                }

                stage('run backend unit tests') {
                    bat "$props.VENV_ACTIVATE_CMD && python manage.py test"
                }
                // need permissions to create test db
        //         stage('run backend test') {
        //             bat ".\\venv\\Scripts\\activate && python manage.py test --noinput"
        //         }
                stage('run migrations') {
                    bat "$props.VENV_ACTIVATE_CMD && python manage.py migrate"
                }

                dir('.\\ui') {
                    stage('update frontend dependencies') {
                        bat "$props.NPM_PATH\\npm i"
                    }
                    stage("build frontend") {
                        bat "$props.NPM_PATH\\node $props.NPM_PATH\\node_modules\\@angular\\cli\\bin\\ng build -c=ngst-staging"
                    }
                    stage("run e2e tests") {
                         try {
                            configFileProvider([configFile(fileId: 'be366a0d-7ab7-4d10-84c0-9ae3e5442af5', targetLocation: 'cypress.env.json')]) {
                                config = readJSON file: 'cypress.env.json'
                                env.CYPRESS_BASE_URL=config['baseUrl']
                                env.NO_COLOR=1
                                bat "$props.NPM_PATH\\node $props.NPM_PATH\\node_modules\\@angular\\cli\\bin\\ng run ui:cypress-run"
                            }
                         } catch (e) {
                            archiveArtifacts artifacts:'cypress/videos/**/*.mp4'
                            throw e
                         }
                    }
                }
           }
            stage("Approval") {
                slackSend(channel:props.NOTIFICATION_CHANNEL_ID, message: "Account Request Tool Staging Build COMPLETE",
                teamDomain:'innovateinc', botUser:true, tokenCredentialId:'9de5b95a-9ad8-418a-989e-7ae694f3613f')
                input(message: "Approved for merge?")
                // todo: revert migrations on abort
            }
      } catch(Exception e) {
          slackSend(channel:props.NOTIFICATION_CHANNEL_ID, message: "Account Request Tool Staging Build FAILED or SUPERSEDED",
          teamDomain:'innovateinc', botUser:true, tokenCredentialId:'9de5b95a-9ad8-418a-989e-7ae694f3613f')
          slackSend(channel:props.NOTIFICATION_CHANNEL_ID, message: e.message,
          teamDomain:'innovateinc', botUser:true, tokenCredentialId:'9de5b95a-9ad8-418a-989e-7ae694f3613f')
          throw(e)
        }
    }
}
