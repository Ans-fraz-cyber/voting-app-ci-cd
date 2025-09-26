pipeline {
    agent any

    tools {
        // Use the JDK you configured in Jenkins global tools
        jdk 'jdk-21'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git'
            }
        }

        stage('SonarQube Scan') {
            environment {
                // This should match the SonarQube server configuration name in Jenkins
                SONARQUBE_SERVER = 'SonarQube'
            }
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'sonar-scanner'
                }
            }
        }
    }
}
