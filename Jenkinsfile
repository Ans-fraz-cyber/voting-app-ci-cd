pipeline {
    agent any

    environment {
        SONAR_HOME = tool name: "SonarQubeScanner", type: "hudson.plugins.sonar.SonarRunnerInstallation"
        SONARQUBE_TOKEN = credentials('sonarqube-token')
        SONAR_HOST_URL  = 'http://voting-app-sonarqube-1:9000'
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
                    withCredentials([string(credentialsId: 'sonarqube-token', variable: 'TOKEN')]) {
                        sh "${SONAR_HOME}/bin/sonar-scanner -Dsonar.projectName=voting-app -Dsonar.projectKey=voting-app -Dsonar.host.url=${SONAR_HOST_URL} -Dsonar.login=$TOKEN"
                    }
                }
            }
        }

        stage('Build Application') {
            steps {
                echo "🏗️ Building the application"
                nodejs('NodeJS') {
                    sh "npm install"
                    sh "npm run build"
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
} // <-- Make sure this final closing brace exists
