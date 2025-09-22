pipeline {
    agent any
    
    stages {
        stage('Deploy Voting App') {
            steps {
                sh '''
                    echo "=== Deploying Voting App using Host Docker ==="
                    
                    # Change to the correct project directory on host
                    cd /home/ans-fraz/Downloads/voting-app
                    
                    # Stop any running containers
                    docker-compose down || true
                    
                    # Build and start the application
                    docker-compose up --build -d
                    
                    # Wait for services to start
                    sleep 30
                    
                    # Check status
                    echo "=== Deployment Status ==="
                    docker-compose ps
                    echo "Vote app: http://localhost:5000"
                    echo "Result app: http://localhost:5001"
                '''
            }
        }
    }
    
    post {
        success {
            echo "✅ Voting App deployed successfully!"
        }
        failure {
            echo "❌ Deployment failed!"
        }
    }
}
