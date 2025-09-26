pipeline {
    agent any

    environment {
        SONARQUBE_TOKEN = credentials('MySonarQubeServer') // Use the correct token ID
        GITHUB_CREDS    = 'github-creds'
        SONAR_HOST_URL  = 'http://voting-app-sonarqube-1:9000'
    }

    stages {
        stage('Clone Code') {
            steps {
                echo "🔄 Cloning code from main branch"
                git(
                    credentialsId: "${GITHUB_CREDS}",
                    url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git',
                    branch: 'main'
                )
            }
        }

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
