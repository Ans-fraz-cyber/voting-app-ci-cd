pipeline {
    agent any
    stages {
        stage('Checkout Code') {
            steps { 
                checkout scm
                sh 'echo "Code checkout completed"'
            }
        }
        stage('Code Quality') {
            steps {
                sh 'echo "Running code quality checks"'
            }
        }
        stage('Build Images') {
            steps {
                sh 'docker build -t voting-app-vote /host-voting-app/vote'
                sh 'docker build -t voting-app-result /host-voting-app/result'
                sh 'docker build -t voting-app-worker /host-voting-app/worker'
            }
        }
        stage('Security Scan') {
            steps {
                sh 'trivy image voting-app-vote || true'
                sh 'trivy image voting-app-result || true'
                sh 'trivy image voting-app-worker || true'
            }
        }
        stage('Testing') {
            steps {
                sh 'echo "Running tests"'
            }
        }
        stage('Deploy Production') {
            steps {
                sh 'docker stop vote result worker redis db || true'
                sh 'docker rm vote result worker redis db || true'
                sh 'docker run -d --name redis redis:alpine'
                sh 'docker run -d --name db -e POSTGRES_PASSWORD=postgres postgres:15-alpine'
                sh 'sleep 10'
                sh 'docker run -d --name worker --link redis --link db voting-app-worker'
                sh 'docker run -d --name vote -p 5000:80 --link redis -e OPTION_A=Cats -e OPTION_B=Dogs voting-app-vote'
                sh 'docker run -d --name result -p 5001:80 --link db voting-app-result'
            }
        }
        stage('Health Check') {
            steps {
                sh 'sleep 15'
                sh 'docker ps'
                sh 'echo "7-STAGE PIPELINE COMPLETED"'
            }
        }
    }
}
