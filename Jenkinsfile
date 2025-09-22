pipeline {
    agent any
    
    stages {
        stage('Test and Deploy') {
            steps {
                sh '''
                    echo "Testing Docker access..."
                    docker version || echo "Docker not working"
                    
                    echo "Deploying from host directory..."
                    cd /host-voting-app
                    docker-compose version || echo "Using docker commands"
                    
                    # Try docker-compose first, then fallback to docker
                    docker-compose down || true
                    docker-compose up -d || echo "Trying individual commands..."
                    
                    echo "Deployment attempted!"
                '''
            }
        }
    }
}
