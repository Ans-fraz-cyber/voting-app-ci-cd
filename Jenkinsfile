pipeline {
    agent any
    
    stages {
        stage('Deploy Voting App') {
            steps {
                sh '''
                    echo "=== Deploying from Host Directory ==="
                    cd /host-voting-app
                    pwd
                    ls -la
                    docker-compose down || true
                    docker-compose up -d
                    echo "✅ DEPLOYMENT SUCCESSFUL!"
                    docker-compose ps
                '''
            }
        }
    }
}
