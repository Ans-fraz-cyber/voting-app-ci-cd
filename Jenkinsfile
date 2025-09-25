pipeline {
    agent any

    environment {
        SONARQUBE_TOKEN = credentials('sonarqube-token') // Already stored in Jenkins
        SONAR_HOST_URL  = 'http://sonarqube:9000'        // Use container name
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube Scan...'
                withSonarQubeEnv('SonarQubeServer') { // Use the configured Jenkins SonarQube server
                    sh """
                        sonar-scanner \
                            -Dsonar.projectKey=voting-app \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=$SONAR_HOST_URL \
                            -Dsonar.login=$SONARQUBE_TOKEN
                    """
                }
            }
        }

        stage('Build & Deploy Docker') {
            steps {
                echo 'Building and deploying Docker images...'
                sh 'docker compose -f docker-compose.yml build'
                sh 'docker compose -f docker-compose.yml up -d'
            }
        }

        stage('Trivy Scan') {
            steps {
                echo 'Scanning Docker images with Trivy...'
                // Replace these with your actual image names if different
                sh 'trivy image voting-app_vote:latest || true'
                sh 'trivy image voting-app_result:latest || true'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh 'docker compose -f docker-compose.yml down'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Check logs above for details.'
        }
    }
}
