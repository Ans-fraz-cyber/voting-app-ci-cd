pipeline {
    agent any

    tools {
        git 'Default'
    }

    environment {
        SONARQUBE_TOKEN = credentials('sonarqube-token')
        SONAR_HOST_URL = 'http://sonarqube:9000'
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
                sh """
                    ${tool 'SonarQubeScanner'}/bin/sonar-scanner \
                        -Dsonar.projectKey=voting-app \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=$SONAR_HOST_URL \
                        -Dsonar.token=$SONARQUBE_TOKEN
                """
            }
        }

        stage('Build & Deploy with Docker') {
            steps {
                echo 'Building Docker images and starting services...'
                sh 'docker-compose -f docker-compose.yml build'
                sh 'docker-compose -f docker-compose.yml up -d'
            }
        }

        stage('Trivy Scan') {
            steps {
                echo 'Scanning Docker images for vulnerabilities...'
                sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL vote:latest'
                sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL result:latest'
                sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL worker:latest'
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution completed'
        }
        failure {
            echo 'Build failed. Please check logs for details.'
        }
    }
}
