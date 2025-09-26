pipeline {
    agent any

    environment {
        SONAR_HOME = tool "MySonarQubeServer"  // your SonarQube installation name
    }

    stages {
        stage('Clone Code') {
            steps {
                echo "🔄 Cloning code from GitHub"
                git(
                    credentialsId: "github-creds",  // your Jenkins GitHub credentials
                    url: 'https://github.com/eGeeks-Design-and-Development/BrainBench-Web-App.git',
                    branch: 'main'  // change to your desired branch if needed
                )
            }
        }

        stage('SonarQube Quality Analysis') {
            steps {
                withSonarQubeEnv('MySonarQubeServer') {  // must match SonarQube installation name
                    sh """
                        ${SONAR_HOME}/bin/sonar-scanner \
                        -Dsonar.projectName=voting-app \
                        -Dsonar.projectKey=voting-app \
                        -Dsonar.host.url=http://sonarqube:9000 \
                        -Dsonar.login=${SONARQUBE_TOKEN}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed. Check logs above."
        }
    }
}
