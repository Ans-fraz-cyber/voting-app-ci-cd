pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = 'github-creds'
        SONAR_TOKEN = credentials('sonar-token')
    }

    stages {

        stage('Checkout') {
            steps {
                git(
                    branch: 'main',
                    url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git',
                    credentialsId: "${GIT_CREDENTIALS}"
                )
            }
        }

        stage('Build') {
            steps {
                echo 'Building the application...'
                // Example: For Node.js project
                sh 'npm install'
                sh 'npm run build'
            }
        }

        stage('SonarQube Analysis') {
            environment {
                SONAR_HOST_URL = 'http://localhost:9000'  // Your SonarQube URL
            }
            steps {
                echo 'Running SonarQube Scanner...'
                withSonarQubeEnv('Sonar') {
                    sh 'sonar-scanner -Dsonar.login=${SONAR_TOKEN}'
                }
            }
        }

        stage('OWASP Dependency-Check') {
            steps {
                echo 'Running OWASP Dependency-Check...'
                // Assuming you installed Dependency-Check plugin
                dependencyCheck additionalArguments: '--scan . --format HTML'
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                // Example: For Node.js project
                sh 'npm test'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
