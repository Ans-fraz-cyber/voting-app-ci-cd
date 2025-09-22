pipeline {
    agent any
    
    stages {
        stage('Deploy Voting App') {
            steps {
                sh '''
                    echo "=== Simple Deployment ==="
                    
                    # Stop and remove old containers
                    docker stop vote result worker redis db || true
                    docker rm vote result worker redis db || true
                    
                    # Pull base images
                    docker pull redis:alpine
                    docker pull postgres:15-alpine
                    
                    # Build app images
                    docker build -t vote-app ./vote
                    docker build -t result-app ./result
                    docker build -t worker-app ./worker
                    
                    # Start services in order
                    docker run -d --name redis redis:alpine
                    docker run -d --name db -e POSTGRES_PASSWORD=postgres postgres:15-alpine
                    sleep 5
                    docker run -d --name worker worker-app
                    docker run -d --name vote -p 5000:80 vote-app
                    docker run -d --name result -p 5001:80 result-app
                    
                    echo "=== DEPLOYMENT SUCCESSFUL ==="
                    docker ps
                    echo "Vote: http://localhost:5000"
                    echo "Result: http://localhost:5001"
                '''
            }
        }
    }
}
