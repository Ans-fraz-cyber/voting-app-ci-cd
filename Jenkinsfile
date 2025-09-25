pipeline {
    agent any

    tools {
        // Ensure Git and SonarQube Scanner are available
        git 'Default'
    }

    environment {
        SONARQUBE = credentials('sonarqube-token')
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
                withSonarQubeEnv('MySonarQubeServer') {
                    withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                        sh """
                            ${tool 'SonarQubeScanner'}/bin/sonar-scanner \
                                -Dsonar.projectKey=voting-app \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=http://sonarqube:9000 \
                                -Dsonar.token=$SONAR_TOKEN
                        """
                    }
                }
            }
        }

        stage('Build & Deploy with Docker') {
            steps {
                echo 'Building Docker images and starting services...'
                sh 'docker-compose -f docker-compose.yml build'
                sh 'docker-compose -f docker-compose.yml up -d'
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
