pipeline {
    agent any

    environment {
        // Jenkins SonarQube Scanner tool
        SONAR_HOME = tool name: "SonarQubeScanner", type: "hudson.plugins.sonar.SonarRunnerInstallation"
        // SonarQube token stored in Jenkins credentials
        SONARQUBE_TOKEN = credentials('sonarqube-token')
        // SonarQube container URL (use container name, not localhost)
        SONAR_HOST_URL  = 'http://voting-app-sonarqube-1:9000'
        // GitHub credentials ID for cloning repo
        GITHUB_CREDS    = 'github-creds'
    }

    stages {
        stage('Clone Code') {
            steps {
                echo "🔄 Cloning code from main branch"
                git(
                    credentialsId: "${GITHUB_CREDS}",
                    url: 'https://github.com/Ans-fraz-cyber/voting-app-ci-cd.git',
                    branch: 'main'
                )
            }
        }

        stage('SonarQube Quality Analysis') {
            steps {
                echo "🔍 Running SonarQube analysis"
                withSonarQubeEnv('MySonarQubeServer') { 
                    sh """
                        ${SONAR_HOME}/bin/sonar-scanner \
                        -Dsonar.projectName=voting-app \
                        -Dsonar.projectKey=voting-app \
                        -Dsonar.host.url=$SONAR_HOST_URL \
                        -Dsonar.login=$SONARQUBE_TOKEN
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed. Check logs above."
        }
    }
}
