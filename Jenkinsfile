pipeline {
    agent any
    
    stages {
        stage('Deploy Voting App') {
            steps {
                sh '''
                    echo "=== Current Workspace ==="
                    pwd
                    ls -la
                    
                    echo "=== Deploying Application ==="
                    # Use current directory (workspace where code is cloned)
                    docker-compose down || true
                    docker-compose up --build -d
                    
                    sleep 30
                    
                    echo "=== Deployment Status ==="
                    docker-compose ps
                    echo "✅ Voting App deployed successfully!"
                    echo "Vote: http://localhost:5000"
                    echo "Results: http://localhost:5001"
                '''
            }
        }
    }
}
