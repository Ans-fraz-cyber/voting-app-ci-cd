pipeline {
    agent any

    environment {
        SONAR_HOME = tool "SonarQubeScanner"   // must match the tool name in Jenkins
    }

    stages {
        stage('Code Clone') {
            steps {
                echo "🔄 Cloning repository..."
                git branch: 'main', url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "🔍 Running SonarQube Analysis..."
                withSonarQubeEnv('SonarQubeServer') { // must match Jenkins SonarQube server config name
                    sh """
                        ${SONAR_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=voting-app \
                        -Dsonar.projectName=voting-app \
                        -Dsonar.sources=.
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
            echo "❌ Pipeline failed!"
        }
    }
}
