// abort existing build
def buildNumber = env.BUILD_NUMBER as int
if (buildNumber > 1) milestone(buildNumber - 1)
milestone(buildNumber)

node {
    dir('D:\\R9Web\\GeoPlatform-Request-Tool-Staging') {
        checkout scm
        stage('update backend dependencies') {
            bat ".\\venv\\Scripts\\activate && pip install -r requirements.txt"
        }
        // need permissions to create test db
//         stage('run backend test') {
//             bat ".\\venv\\Scripts\\activate && python manage.py test --noinput"
//         }
        stage('run migrations') {
            bat ".\\venv\\scripts\\activate && python manage.py migrate"
        }
    }
    dir('.\\ui') {
        stage('update frontend dependencies') {
            bat "npm i"
        }
        stage("build frontend") {
            bat "npm run build:staging"
        }
    }
    stage("Approval") {
        input(message: "Approved for merge?")
        // todo: revert migrations on abort
    }
}