pipeline {
    agent any

    environment {
        SCANNER_HOME = tool 'SonarQubeScanner'   // must match the name in Jenkins Global Tool Configuration
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "Running SonarQube Scan..."
                withSonarQubeEnv('MySonarQubeServer') {   // must match the name in Jenkins > Configure System > SonarQube servers
                    withCredentials([string(credentialsId: 'Sonar', variable: 'SONAR_AUTH_TOKEN')]) {
                        sh '''
                            $SCANNER_HOME/bin/sonar-scanner \
                            -Dsonar.projectKey=voting-app \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=$SONAR_HOST_URL \
                            -Dsonar.login=$SONAR_AUTH_TOKEN
                        '''
                    }
                }
            }
        }

        stage('Build & Deploy with Docker') {
            steps {
                echo "Building Docker images and starting services..."
                sh 'docker-compose -f docker-compose.yml build'
                sh 'docker-compose -f docker-compose.yml up -d'
            }
        }
    }

    post {
        always {
            echo "Pipeline execution completed"
        }
        success {
            echo "Build succeeded. Check SonarQube dashboard for analysis report."
        }
        failure {
            echo "Build failed. Please check logs for details."
        }
    }
}
