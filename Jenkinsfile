pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = 'github-creds'
        SONAR_TOKEN     = credentials('sonar-token')
        DOCKER_IMAGE    = "voting-app:latest" // Local Docker image
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git',
                    credentialsId: "${GIT_CREDENTIALS}"
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('Sonar') {
                    sh "sonar-scanner -Dsonar.login=${SONAR_TOKEN}"
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
                // OWASP Dependency-Check scan with configured tool
                dependencyCheck additionalArguments: '--scan . --format HTML', odcInstallation: 'ODC'

                // Trivy scan for Docker image vulnerabilities
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
