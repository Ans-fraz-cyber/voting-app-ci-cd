	pipeline {
    agent any

    environment {
        SONAR_HOME = tool name: "SonarQubeScanner", type: "hudson.plugins.sonar.SonarRunnerInstallation"
        SONARQUBE_TOKEN = credentials('sonarqube-token')
        // This must be the Docker container name, NOT localhost
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
                    // Pass the token securely as an argument
                    withCredentials([string(credentialsId: 'sonarqube-token', variable: 'TOKEN')]) {
    sh "${SONAR_HOME}/bin/sonar-scanner -Dsonar.projectName=voting-app -Dsonar.projectKey=voting-app -Dsonar.host.url=${SONAR_HOST_URL} -Dsonar.login=$TOKEN"
}

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

