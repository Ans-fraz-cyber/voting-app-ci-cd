pipeline {
    agent any
    
    environment {
        SONARQUBE_URL = 'http://localhost:9000'
        SONARQUBE_SCANNER_HOME = tool 'SonarQubeScanner'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    withSonarQubeEnv('sonarqube') {
                        sh """
                            ${SONARQUBE_SCANNER_HOME}/bin/sonar-scanner \
                            -Dsonar.projectKey=voting-app \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=${SONARQUBE_URL} \
                            -Dsonar.login=admin \
                            -Dsonar.password=admin
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "SonarQube analysis completed. Check results at ${SONARQUBE_URL}"
        }
    }
}
