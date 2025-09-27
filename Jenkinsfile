pipeline {
    agent any

    environment {
        SONARQUBE = 'SonarQubeServer'        // must match the name in Jenkins > Configure System
        SONAR_AUTH_TOKEN = credentials('sonar-token')  // 👈 maps your Jenkins credential ID
    }

    stages {
        stage('Code Clone') {
            steps {
                echo "🔄 Cloning repository..."
                git url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git', branch: 'main'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "🔍 Running SonarQube Analysis..."
                withSonarQubeEnv("${SONARQUBE}") {
                    script {
                        def scannerHome = tool 'SonarQubeScanner'   // must match the name in Global Tool Configuration
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                              -Dsonar.projectKey=voting-app \
                              -Dsonar.projectName=voting-app \
                              -Dsonar.sources=. \
                              -Dsonar.login=${SONAR_AUTH_TOKEN}
                        """
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "🐳 Building Docker images for vote, result, and worker..."
                sh '''
                    docker build -t voting-app-vote:latest ./vote
                    docker build -t voting-app-result:latest ./result
                    docker build -t voting-app-worker:latest ./worker
                '''
            }
        }

        stage('Trivy Scan') {
            steps {
                echo "🔎 Running Trivy vulnerability scan on all services..."
                sh '''
                    trivy image --exit-code 0 --severity HIGH,CRITICAL voting-app-vote:latest
                    trivy image --exit-code 0 --severity HIGH,CRITICAL voting-app-result:latest
                    trivy image --exit-code 0 --severity HIGH,CRITICAL voting-app-worker:latest
                '''
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
