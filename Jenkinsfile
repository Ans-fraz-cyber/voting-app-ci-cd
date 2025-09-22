pipeline {
    agent any
    
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                sh 'echo "Code checked out successfully"'
            }
        }
        
        stage('Deploy Voting App') {
            steps {
                sh '''
                    # Use host Docker to deploy the application
                    cd /var/jenkins_home/workspace/voting-app-pipeline
                    docker-compose down || true
                    docker-compose up --build -d
                    
                    # Wait for services to start
                    sleep 30
                    
                    # Check status
                    echo "=== Running Containers ==="
                    docker-compose ps
                    
                    echo "=== Application URLs ==="
                    echo "Vote app: http://localhost:5000"
                    echo "Result app: http://localhost:5001"
                '''
            }
        }
    }
    
    post {
        success {
            echo "✅ Voting App deployed successfully!"
            sh '''
                echo "Access your application at:"
                echo "Vote: http://$(hostname -I | awk "{print \$1}"):5000"
                echo "Results: http://$(hostname -I | awk "{print \$1}"):5001"
            '''
        }
        failure {
            echo "❌ Deployment failed!"
        }
    }
}
