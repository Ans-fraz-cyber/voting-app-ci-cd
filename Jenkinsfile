pipeline {
    agent any

    environment {
        SONARQUBE_TOKEN = credentials('MySonarQubeServer') // Jenkins credentials for SonarQube token
        SONAR_HOST_URL  = 'http://voting-app-sonarqube-1:9000'
    }

    stages {
        stage('SonarQube Quality Analysis') {
            steps {
                echo "🔍 Running SonarQube analysis"
                withSonarQubeEnv('MySonarQubeServer') {
                    sh """
                        ${tool name: 'SonarQubeScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'}/bin/sonar-scanner \
                        -Dsonar.projectName=voting-app \
                        -Dsonar.projectKey=voting-app \
                        -Dsonar.host.url=${SONAR_HOST_URL} \
                        -Dsonar.token=${SONARQUBE_TOKEN}
                    """
                }
            }
        }

        stage('Build Application') {
            steps {
                echo "🏗️ Building the application using Docker Compose on host"
                sh '''
                    # Use host Docker via mounted socket
                    DOCKER_HOST=unix:///var/run/docker.sock docker-compose up --build -d
                '''
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
