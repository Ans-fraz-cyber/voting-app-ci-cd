pipeline {
    agent any
    
    environment {
        VOTE_PORT = '5080'
        RESULT_PORT = '5081'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        
        stage('Deploy Application') {
            steps {
                sh 'docker-compose down || true'
                sh "sed -i 's/8080:80/${VOTE_PORT}:80/g' docker-compose.yml"
                sh "sed -i 's/8081:80/${RESULT_PORT}:80/g' docker-compose.yml"
                sh 'docker-compose up -d'
                sleep 15
            }
        }
    }
    
    post {
        always {
            sh 'docker-compose ps'
        }
    }
}
