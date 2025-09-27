pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "voting-app:latest"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git',
                    credentialsId: 'github-creds'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                // Uses Sonar container directly
                withSonarQubeEnv('Sonar') {
                    sh "sonar-scanner"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}")
                }
            }
        }

        stage('Security Scan') {
            steps {
                // OWASP Dependency-Check
                dependencyCheck additionalArguments: '--scan . --format HTML', odcInstallation: 'ODC'

                // Trivy image scan
                sh "trivy image --exit-code 1 --severity HIGH,CRITICAL ${DOCKER_IMAGE}"
            }
        }

    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs!'
        }
    }
}
