pipeline {
    agent any

    tools {
        // Match the names exactly in Jenkins Global Tool Configuration
        jdk 'jdk-21'
        maven 'Maven'
        git 'Default'
        sonarQube 'Sonar'
    }

    environment {
        // Jenkins credentials IDs
        GIT_CREDENTIALS = 'github-creds'
        SONAR_TOKEN     = credentials('sonar-token')
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git',
                    credentialsId: "${GIT_CREDENTIALS}"
            }
        }

        stage('Maven Build') {
            steps {
                sh 'mvn clean install'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('Sonar') {
                    sh "mvn sonar:sonar -Dsonar.login=${SONAR_TOKEN}"
                }
            }
        }

        stage('OWASP Dependency Check') {
            steps {
                dependencyCheck odcInstallation: 'ODC',
                                additionalArguments: '--scan . --format HTML'
            }
        }

    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check the logs!'
        }
    }
}
