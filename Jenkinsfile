pipeline {
    agent {
        docker { image 'openjdk:21' } // container has correct JDK
    }
    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git'
            }
        }
        stage('SonarQube Scan') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'sonar-scanner'
                }
            }
        }
    }
}
