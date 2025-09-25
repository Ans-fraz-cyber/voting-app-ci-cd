pipeline {
    agent any

    environment {
        SONARQUBE_TOKEN = credentials('sonarqube-token')
        SONAR_HOST_URL  = 'http://sonarqube:9000'
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
                        -Dsonar.login=$SONARQUBE_TOKEN \
                        -Dsonar.qualitygate.wait=false
                """
            }
        }

        stage('Build & Deploy Docker') {
            steps {
                echo 'Building Docker images and starting services...'
                sh 'docker-compose -f docker-compose.yml build'
                sh 'docker-compose -f docker-compose.yml up -d'
            }
        }

        stage('Trivy Scan') {
            steps {
                echo 'Scanning Docker images with Trivy...'
                // Replace these with your actual image names
                sh 'trivy image voting-app_vote:latest'
                sh 'trivy image voting-app_result:latest'
            }
        }
    }
}
