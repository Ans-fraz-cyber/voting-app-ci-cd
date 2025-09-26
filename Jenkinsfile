pipeline {
    agent any

    tools {
        jdk 'jdk-17' // Name you gave in Jenkins global tools
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git'
            }
        }

        stage('SonarQube Scan') {
            environment {
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
