pipeline {
    agent any

    environment {
        // Jenkins credential IDs
        SONARQUBE_TOKEN = credentials('MySonarQubeToken')   // token only
        SONARQUBE_SERVER = 'MySonarQubeServer'              // SonarQube server config (from Jenkins → Manage Jenkins → Configure System)
        SONAR_HOST_URL  = 'http://voting-app-sonarqube-1:9000'
    }

    stages {
        stage('Checkout') {
            steps {
                echo "📥 Code already checked out by Jenkins (Pipeline from SCM)"
                sh 'ls -l'  // confirm files exist
            }
        }

        stage('SonarQube Quality Analysis') {
            steps {
                echo "🔍 Running SonarQube analysis"
                withSonarQubeEnv("${SONARQUBE_SERVER}") {
                    sh """
                        ${tool name: 'SonarQubeScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'}/bin/sonar-scanner \
                        -Dsonar.projectKey=voting-app \
                        -Dsonar.projectName=voting-app \
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
