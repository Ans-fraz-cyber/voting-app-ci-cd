pipeline {
    agent any
    
    environment {
        SONARQUBE_TOKEN = credentials('sonarqube-token')
        SONAR_HOST_URL  = 'http://sonarqube:9000'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Quality Analysis') {
            steps {
                withSonarQubeEnv('MySonarQubeServer') {
                    sh """
                        sonar-scanner \
                            -Dsonar.projectName=voting-app \
                            -Dsonar.projectKey=voting-app \
                            -Dsonar.host.url=$SONAR_HOST_URL \
                            -Dsonar.login=$SONARQUBE_TOKEN
                    """
                }
            }
        }

        stage('Trivy File System Scan') {
            steps {
                sh "trivy fs --format table -o trivy-fs-report.html . || true"
            }
        }

        stage('Build & Deploy using Docker compose') {
            steps {
                sh "docker compose -f docker-compose.yml build"
                sh "docker compose -f docker-compose.yml up -d"
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh "trivy image voting-app_vote:latest || true"
                sh "trivy image voting-app_result:latest || true"
                sh "trivy image voting-app_worker:latest || true"
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh 'docker compose -f docker-compose.yml down || true'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Check logs above for details.'
        }
    }
}
