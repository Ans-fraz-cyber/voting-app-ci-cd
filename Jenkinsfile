pipeline {
    agent any

    tools {
        // Make sure these names exactly match your Global Tool Configuration
        jdk 'jdk-21'
        maven 'Maven'        // Your Maven installation name
        git 'Default'         // Your Git installation name
        dependencyCheck 'ODC' // Name you gave for OWASP Dependency-Check
        sonarQube 'Sonar'     // SonarQube Scanner installation name
    }

    environment {
        // Use Jenkins credentials IDs
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
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs.'
        }
    }
}
